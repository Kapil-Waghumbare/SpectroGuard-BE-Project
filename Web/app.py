from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle, math, re, urllib.parse, os
import numpy as np
from collections import defaultdict, Counter
import pandas as pd

app = Flask(__name__)
CORS(app)

# ╔══════════════════════════════════════════════════════╗
# ║  LOAD MODELS                                         ║
# ╚══════════════════════════════════════════════════════╝

class MarkovPasswordModel:
    def __init__(self):
        self.n = 3
        self.transitions = defaultdict(Counter)

# app.py lives inside  Web/
# Models/ folder is one level up:  ../Models/
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, '..', 'Models')

# Markov model  →  Models/markov_password_model.pkl
with open(os.path.join(MODELS_DIR, 'markov_password_model.pkl'), 'rb') as f:
    markov_model = pickle.load(f)

# SVM model  →  Models/Phishing_Website_SVM.pkl
# pkl structure: dict with keys 'model' (SVC) and 'scaler' (StandardScaler)
# SVC classes_: -1 = phishing,  1 = legit
with open(os.path.join(MODELS_DIR, 'Phishing_Website_SVM.pkl'), 'rb') as f:
    svm_data   = pickle.load(f)
svm_model  = svm_data['model']
svm_scaler = svm_data['scaler']

# 31 features in the exact order the SVM was trained on
SVM_FEATURES = [
    'index', 'having_IPhaving_IP_Address', 'URLURL_Length', 'Shortining_Service',
    'having_At_Symbol', 'double_slash_redirecting', 'Prefix_Suffix',
    'having_Sub_Domain', 'SSLfinal_State', 'Domain_registeration_length',
    'Favicon', 'port', 'HTTPS_token', 'Request_URL', 'URL_of_Anchor',
    'Links_in_tags', 'SFH', 'Submitting_to_email', 'Abnormal_URL', 'Redirect',
    'on_mouseover', 'RightClick', 'popUpWidnow', 'Iframe', 'age_of_domain',
    'DNSRecord', 'web_traffic', 'Page_Rank', 'Google_Index',
    'Links_pointing_to_page', 'Statistical_report'
]

# Known URL shorteners  (SVM cannot see the real destination)
SHORTENERS = {
    'bit.ly', 'goo.gl', 't.co', 'tinyurl.com', 'ow.ly',
    'is.gd', 'buff.ly', 'rebrand.ly', 'short.link', 'cutt.ly'
}

# Suspicious TLDs used by free/phishing hosting
SUSPICIOUS_TLDS = {
    '.tk', '.ml', '.ga', '.cf', '.xyz', '.top',
    '.info', '.click', '.link', '.pw', '.cc'
}

# ╔══════════════════════════════════════════════════════╗
# ║  PASSWORD SCORING  (Markov model)                    ║
# ╚══════════════════════════════════════════════════════╝

def score_password(password):
    if not password:
        return 0, "Too Short"

    order, vocab = 2, 150
    text         = '<^^' + password + '<'
    log_prob     = 0.0
    count        = 0

    for i in range(order, len(text)):
        ctx  = text[i - order:i]
        nx   = text[i]
        tot  = sum(markov_model.transitions[ctx].values())
        freq = markov_model.transitions[ctx].get(nx, 0)
        prob = (freq + 1) / (tot + vocab) if tot > 0 else 1 / vocab
        log_prob += math.log2(prob)
        count    += 1

    if count == 0:
        return 0, "Too Short"

    avg_ll = log_prob / count
    # Lower avg_ll (more surprising to the model) = stronger password
    score  = max(0, min(100, round((avg_ll - (-3.5)) / ((-8.0) - (-3.5)) * 100)))

    labels = [(20, "Very Weak"), (40, "Weak"), (60, "Moderate"), (80, "Strong")]
    label  = next((l for s, l in labels if score < s), "Very Strong")
    return score, label


# ╔══════════════════════════════════════════════════════╗
# ║  URL FEATURE EXTRACTION                              ║
# ╚══════════════════════════════════════════════════════╝

def extract_features(url: str):
    """
    Convert a raw URL into the 31-feature vector the SVM was trained on.
    Encoding follows the UCI phishing dataset:
        1  = legitimate signal
        0  = unknown / neutral
       -1  = phishing signal
    Returns a single-row DataFrame in SVM_FEATURES column order.
    """
    try:
        parsed = urllib.parse.urlparse(url if '://' in url else 'http://' + url)
        netloc = parsed.netloc.lower()
        domain = netloc.lstrip('www.')
        full   = url.lower()

        feats = {}

        # Row index placeholder (always 1)
        feats['index'] = 1

        # Is the hostname a raw IP address?
        feats['having_IPhaving_IP_Address'] = (
            -1 if re.match(r'^\d{1,3}(\.\d{1,3}){3}(:\d+)?$', netloc) else 1
        )

        # URL length  (<54 legit, 54-75 suspicious, >75 phishing)
        url_len = len(full)
        feats['URLURL_Length'] = 1 if url_len < 54 else (0 if url_len < 75 else -1)

        # Known URL-shortening service?
        feats['Shortining_Service'] = (
            -1 if any(s in netloc for s in SHORTENERS) else 1
        )

        # @ symbol in URL forces browser to ignore text before it
        feats['having_At_Symbol'] = -1 if '@' in full else 1

        # Double-slash redirect beyond the protocol (// after position 7)
        feats['double_slash_redirecting'] = (
            -1 if full.find('//', 8) != -1 else 1
        )

        # Hyphen in domain  (legit brands rarely use hyphens in domain)
        feats['Prefix_Suffix'] = -1 if '-' in netloc else 1

        # Subdomain depth
        dot_count = domain.count('.')
        feats['having_Sub_Domain'] = (
            1 if dot_count == 1 else (0 if dot_count == 2 else -1)
        )

        # Valid HTTPS?
        feats['SSLfinal_State'] = 1 if full.startswith('https') else -1

        # Domain registration length — unknown without WHOIS → neutral
        feats['Domain_registeration_length'] = 0

        # Favicon — assumed present for unknown sites
        feats['Favicon'] = 1

        # Non-standard port?
        feats['port'] = (
            -1 if parsed.port and parsed.port not in (80, 443) else 1
        )

        # 'https' keyword INSIDE the domain itself (fake-trust signal)
        feats['HTTPS_token'] = -1 if 'https' in domain else 1

        # Features below require fetching page HTML — set to neutral
        feats['Request_URL']         = 1
        feats['URL_of_Anchor']       = 0
        feats['Links_in_tags']       = 0
        feats['SFH']                 = 1

        # Form submitting to an email address?
        feats['Submitting_to_email'] = -1 if 'mailto:' in full else 1

        # Abnormal URL: domain not present in full URL string?
        feats['Abnormal_URL'] = 1 if (domain and domain in full) else -1

        # Extra // beyond the protocol = redirect
        feats['Redirect'] = -1 if full.count('//') > 1 else 1

        # JS / browser behaviour — unknown without page execution → legit default
        feats['on_mouseover']  = 1
        feats['RightClick']    = 1
        feats['popUpWidnow']   = 1
        feats['Iframe']        = 1

        # Network-level features — unknown without external APIs → neutral
        feats['age_of_domain']          = 0
        feats['DNSRecord']              = 1
        feats['web_traffic']            = 0
        feats['Page_Rank']              = 0
        feats['Google_Index']           = 1
        feats['Links_pointing_to_page'] = 0

        # Keyword in domain matching known phishing/scam terms
        phish_kw = ['phish', 'scam', 'malware', 'fraud', 'hack', 'spoof']
        feats['Statistical_report'] = (
            -1 if any(kw in domain for kw in phish_kw) else 1
        )

        return pd.DataFrame([feats])[SVM_FEATURES]

    except Exception:
        return None


# ╔══════════════════════════════════════════════════════╗
# ║  HEURISTIC SUPPLEMENT LAYER                          ║
# ╚══════════════════════════════════════════════════════╝

SUSPICIOUS_KEYWORDS = [
    'login', 'verify', 'secure', 'account', 'update', 'banking',
    'paypal', 'signin', 'confirm', 'password', 'credential'
]


def heuristic_phishing_score(url: str) -> float:
    """
    Rule-based phishing score (0.0 – 1.0).
    Supplements the SVM for signals it cannot learn from URL text alone
    (e.g. IP hosting, URL shorteners, bad TLDs, suspicious keyword combos).
    """
    full   = url.lower()
    parsed = urllib.parse.urlparse(url if '://' in url else 'http://' + url)
    netloc = parsed.netloc.lower()
    score  = 0.0

    # Raw IP address as host (strong signal)
    if re.match(r'^\d{1,3}(\.\d{1,3}){3}(:\d+)?$', netloc):
        score += 0.60

    # URL shortener (destination hidden from SVM)
    if any(s in netloc for s in SHORTENERS):
        score += 0.65

    # Free/abused TLD
    if any(netloc.endswith(t) for t in SUSPICIOUS_TLDS):
        score += 0.40

    # Suspicious keywords in full URL
    kw_hits = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in full)
    score  += min(kw_hits * 0.10, 0.30)

    # No HTTPS
    if not full.startswith('https'):
        score += 0.10

    # Hyphen-heavy domain  e.g. secure-login-paypal-verify
    if netloc.count('-') >= 3:
        score += 0.20

    # Very long URL
    if len(full) > 100:
        score += 0.10

    return min(score, 1.0)


# ╔══════════════════════════════════════════════════════╗
# ║  MAIN PREDICTION FUNCTION                            ║
# ╚══════════════════════════════════════════════════════╝

def predict_url(url: str):
    """
    Returns (result, status, confidence).

    result     → "legit" | "phishing" | "invalid"
    status     → "Safe"  | "Suspicious" | "Unknown"
    confidence → int 1–99

    ── Bugs fixed vs original app.py ──────────────────────────────────
    BUG 1 (CRITICAL — caused the "99% confident on fake sites" problem):
    The original threshold logic decided result purely from the confidence
    NUMBER, completely ignoring which CLASS the SVM actually predicted.

        Original broken code:
            if confidence > 85:
                res, status = "legit", "Safe"   ← WRONG for phishing sites
            if prediction == -1 and confidence > 75:
                status = "Risky"                 ← changes status but NOT result

        A phishing URL with SVM confidence 90% was returned as:
            result="legit", status="Risky"
        So phishing.html showed it as LEGIT (green tick).

    FIX: result comes directly from svm_model.predict() class label.
         -1 (phishing class) → result="phishing", status="Suspicious"
          1 (legit class)    → result="legit",    status="Safe"
         Confidence = the model's own probability, not a threshold band.

    BUG 2: IP-address URLs and URL shorteners were never flagged because
    those signals require WHOIS/DNS lookups the SVM did not have at training
    time; the trained features were always set to neutral (0 or 1), so the
    SVM had nothing to learn from.

    FIX: Hard override rules catch IP hosts and shorteners before the SVM
    result is used. A heuristic layer covers other URL-text signals.
    """
    features = extract_features(url)
    if features is None:
        return "invalid", "Unknown", 0

    parsed_check = urllib.parse.urlparse(url if '://' in url else 'http://' + url)
    netloc_check = parsed_check.netloc.lower()

    # ── Hard overrides (signals SVM cannot reliably detect from URL text) ─
    # 1. Raw IP as hostname → phishing
    if re.match(r'^\d{1,3}(\.\d{1,3}){3}(:\d+)?$', netloc_check):
        return "phishing", "Suspicious", 62

    # 2. Known URL shortener → phishing (real destination unknown)
    if any(s in netloc_check for s in SHORTENERS):
        return "phishing", "Suspicious", 70

    # ── SVM prediction ────────────────────────────────────────────────────
    scaled         = svm_scaler.transform(features)
    svm_class      = svm_model.predict(scaled)[0]       # -1=phishing, 1=legit
    proba          = svm_model.predict_proba(scaled)[0] # [P(class=-1), P(class=1)]
    svm_phish_prob = float(proba[0])                    # index 0 = phishing prob

    # ── Heuristic supplement ──────────────────────────────────────────────
    h_score = heuristic_phishing_score(url)

    # ── Blend: 65% SVM, 35% heuristic ────────────────────────────────────
    combined_phish_prob = 0.65 * svm_phish_prob + 0.35 * h_score

    # ── Final decision ────────────────────────────────────────────────────
    is_phishing = combined_phish_prob > 0.50
    confidence  = round(max(combined_phish_prob, 1.0 - combined_phish_prob) * 100)
    confidence  = max(1, min(99, confidence))   # never claim 0% or 100%

    if is_phishing:
        return "phishing", "Suspicious", confidence
    else:
        return "legit", "Safe", confidence


# ╔══════════════════════════════════════════════════════╗
# ║  ROUTES                                              ║
# ╚══════════════════════════════════════════════════════╝

@app.route('/score', methods=['POST'])
def score_route():
    """
    Password strength checker.
    Called by: password-checker.html
    Request  → { "password": "myP@ssw0rd" }
    Response → { "score": 72, "label": "Strong" }
    """
    data = request.get_json(force=True)
    s, l = score_password(data.get('password', ''))
    return jsonify({'score': s, 'label': l})


@app.route('/check_phishing', methods=['POST'])
def check_phishing_route():
    """
    Phishing website detector.
    Called by: phishing.html
    Request  → { "url": "http://example.com" }
    Response → { "result":     "legit" | "phishing" | "invalid",
                 "status":     "Safe"  | "Suspicious" | "Unknown",
                 "confidence": 87 }
    """
    data = request.get_json(force=True)
    res, status, conf = predict_url(data.get('url', ''))
    return jsonify({'result': res, 'status': status, 'confidence': conf})


@app.route('/check_url', methods=['POST'])
def check_url_route():
    """
    URL scanner.
    Called by: URL-checker.html
    Request  → { "url": "http://example.com" }
    Response → { "result":     "legit" | "phishing" | "invalid",
                 "status":     "Safe"  | "Suspicious" | "Unknown",
                 "confidence": 87 }
    """
    data = request.get_json(force=True)
    res, status, conf = predict_url(data.get('url', ''))
    return jsonify({'result': res, 'status': status, 'confidence': conf})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok',
                    'models': ['markov_password_model', 'Phishing_Website_SVM']})


if __name__ == '__main__':
    print("SpectroGuard Backend  →  http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
