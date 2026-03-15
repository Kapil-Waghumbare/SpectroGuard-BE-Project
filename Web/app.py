from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle, math, re, urllib.parse
import numpy as np
from collections import defaultdict, Counter
import pandas as pd

app = Flask(__name__)
CORS(app)

# ╔══════════════════════════════════════════════════════╗
# ║  LOAD MODELS                                         ║
# ╚══════════════════════════════════════════════════════╝

# ── Markov password model ──────────────────────────────
class MarkovPasswordModel:
    def __init__(self):
        self.n = 3
        self.transitions = defaultdict(Counter)

import os
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, '..', 'Models')

with open(os.path.join(MODELS_DIR, 'markov_password_model.pkl'), 'rb') as f:
    markov_model = pickle.load(f)
print("✓ Markov model loaded. States:", len(markov_model.transitions))

# ── SVM phishing model (used for BOTH website & URL) ──
with open(os.path.join(MODELS_DIR, 'Phishing_Website_SVM.pkl'), 'rb') as f:
    svm_data = pickle.load(f)
svm_model  = svm_data['model']
svm_scaler = svm_data['scaler']
print("✓ SVM model loaded. Features:", svm_model.n_features_in_)

# Feature order expected by model
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

# ╔══════════════════════════════════════════════════════╗
# ║  PASSWORD SCORING (Markov)                           ║
# ╚══════════════════════════════════════════════════════╝
def score_password(password):
    if not password:
        return 0, "Too Short"

    order = 2
    text  = '<^^' + password + '<'
    log_prob = 0.0
    count    = 0
    vocab    = 150

    for i in range(order, len(text)):
        ctx  = text[i-order:i]
        nx   = text[i]
        tot  = sum(markov_model.transitions[ctx].values())
        freq = markov_model.transitions[ctx].get(nx, 0)
        prob = (freq + 1) / (tot + vocab) if tot > 0 else 1 / vocab
        log_prob += math.log2(prob)
        count    += 1

    if count == 0:
        return 0, "Too Short"

    avg_ll = log_prob / count
    lo, hi = -3.5, -8.0
    score  = (avg_ll - lo) / (hi - lo) * 100
    score  = max(0, min(100, round(score)))

    if   score < 20: label = "Very Weak"
    elif score < 40: label = "Weak"
    elif score < 60: label = "Moderate"
    elif score < 80: label = "Strong"
    else:            label = "Very Strong"

    return score, label

# ╔══════════════════════════════════════════════════════╗
# ║  URL FEATURE EXTRACTION (for SVM)                    ║
# ╚══════════════════════════════════════════════════════╝
def extract_features(url):
    """
    Extract the 31 features the SVM was trained on from a raw URL string.
    Values: -1 = phishing indicator, 0 = suspicious, 1 = legit
    """
    try:
        parsed = urllib.parse.urlparse(url if '://' in url else 'http://' + url)
        domain = parsed.netloc.lower()
        path   = parsed.path.lower()
        full   = url.lower()
    except Exception:
        return None

    def has_ip(d):
        return -1 if re.match(r'\d+\.\d+\.\d+\.\d+', d) else 1

    def url_length(u):
        l = len(u)
        if l < 54:   return 1
        if l < 75:   return 0
        return -1

    def shortening(u):
        shorts = ['bit.ly','goo.gl','tinyurl','ow.ly','t.co','is.gd','cli.gs','buff.ly']
        return -1 if any(s in u for s in shorts) else 1

    def at_symbol(u):
        return -1 if '@' in u else 1

    def double_slash(u):
        pos = u.find('//')
        return -1 if pos > 7 else 1

    def prefix_suffix(d):
        return -1 if '-' in d else 1

    def sub_domain(d):
        dots = d.count('.')
        if dots == 1: return 1
        if dots == 2: return 0
        return -1

    def ssl_state(u):
        return 1 if u.startswith('https') else -1

    def domain_reg_len():
        return 1  # Can't check WHOIS without external call — default legit

    def favicon():
        return 1  # Default

    def port(u):
        ports = [':21',':22',':23',':80',':443',':445',':8080',':8443']
        return -1 if any(p in u for p in ports[:-2]) else 1

    def https_token(d):
        return -1 if 'https' in d else 1

    def request_url():
        return 1  # No page content available

    def url_of_anchor():
        return 0  # Suspicious default without page

    def links_in_tags():
        return 0

    def sfh():
        return 1

    def submit_email(u):
        return -1 if 'mailto:' in u else 1

    def abnormal_url(d, u):
        return 1 if d in u else -1

    def redirect(u):
        return -1 if u.count('//') > 1 else 1

    def on_mouseover():
        return 1

    def right_click():
        return 1

    def popup():
        return 1

    def iframe():
        return 1

    def age_of_domain():
        return 0  # Unknown without WHOIS

    def dns_record():
        return 1  # Assume exists

    def web_traffic():
        return 0

    def page_rank():
        return 0

    def google_index():
        return 1

    def links_pointing():
        return 0

    def statistical_report(d):
        bad = ['fraud','phish','fake','scam','hack','malware','spam']
        return -1 if any(b in d for b in bad) else 1

    feats = {
        'index': 1,
        'having_IPhaving_IP_Address':   has_ip(domain),
        'URLURL_Length':                url_length(full),
        'Shortining_Service':           shortening(full),
        'having_At_Symbol':             at_symbol(full),
        'double_slash_redirecting':     double_slash(full),
        'Prefix_Suffix':                prefix_suffix(domain),
        'having_Sub_Domain':            sub_domain(domain),
        'SSLfinal_State':               ssl_state(full),
        'Domain_registeration_length':  domain_reg_len(),
        'Favicon':                      favicon(),
        'port':                         port(full),
        'HTTPS_token':                  https_token(domain),
        'Request_URL':                  request_url(),
        'URL_of_Anchor':                url_of_anchor(),
        'Links_in_tags':                links_in_tags(),
        'SFH':                          sfh(),
        'Submitting_to_email':          submit_email(full),
        'Abnormal_URL':                 abnormal_url(domain, full),
        'Redirect':                     redirect(full),
        'on_mouseover':                 on_mouseover(),
        'RightClick':                   right_click(),
        'popUpWidnow':                  popup(),
        'Iframe':                       iframe(),
        'age_of_domain':                age_of_domain(),
        'DNSRecord':                    dns_record(),
        'web_traffic':                  web_traffic(),
        'Page_Rank':                    page_rank(),
        'Google_Index':                 google_index(),
        'Links_pointing_to_page':       links_pointing(),
        'Statistical_report':           statistical_report(domain),
    }

    return pd.DataFrame([feats])[SVM_FEATURES]

def predict_url(url):
    features = extract_features(url)
    if features is None:
        return "invalid", 0

    scaled     = svm_scaler.transform(features)
    prediction = svm_model.predict(scaled)[0]
    decision   = svm_model.decision_function(scaled)[0]

    # decision > 0 → legit (1), < 0 → phishing (-1)
    # Convert decision score to confidence 0–100
    confidence = min(100, max(0, round(abs(decision) / 3.0 * 100)))

    if prediction == 1:
        return "legit", confidence
    else:
        return "phishing", confidence

# ╔══════════════════════════════════════════════════════╗
# ║  ROUTES                                              ║
# ╚══════════════════════════════════════════════════════╝

@app.route('/score', methods=['POST'])
def score_route():
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({'error': 'No password provided'}), 400
    s, l = score_password(data['password'])
    return jsonify({'score': s, 'label': l})

@app.route('/check_phishing', methods=['POST'])
def check_phishing_route():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400
    result, confidence = predict_url(data['url'])
    return jsonify({'result': result, 'confidence': confidence})

@app.route('/check_url', methods=['POST'])
def check_url_route():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400
    result, confidence = predict_url(data['url'])
    # URL checker returns same SVM result with heuristic label
    if result == 'legit':
        status = 'Safe'
    else:
        status = 'Suspicious'
    return jsonify({'status': status, 'result': result, 'confidence': confidence})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
