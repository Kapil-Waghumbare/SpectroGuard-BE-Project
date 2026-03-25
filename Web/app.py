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

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, '..', 'Models')

# Load Markov
with open(os.path.join(MODELS_DIR, 'markov_password_model.pkl'), 'rb') as f:
    markov_model = pickle.load(f)

# Load SVM
with open(os.path.join(MODELS_DIR, 'Phishing_Website_SVM.pkl'), 'rb') as f:
    svm_data = pickle.load(f)
svm_model  = svm_data['model']
svm_scaler = svm_data['scaler']

# Feature order expected by your SVM
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
# ║  LOGIC FUNCTIONS                                     ║
# ╚══════════════════════════════════════════════════════╝

def score_password(password):
    if not password: return 0, "Too Short"
    order, text, log_prob, count, vocab = 2, '<^^' + password + '<', 0.0, 0, 150
    for i in range(order, len(text)):
        ctx = text[i-order:i]
        nx = text[i]
        tot = sum(markov_model.transitions[ctx].values())
        freq = markov_model.transitions[ctx].get(nx, 0)
        prob = (freq + 1) / (tot + vocab) if tot > 0 else 1 / vocab
        log_prob += math.log2(prob)
        count += 1
    if count == 0: return 0, "Too Short"
    avg_ll = log_prob / count
    score = max(0, min(100, round((avg_ll - (-3.5)) / ((-8.0) - (-3.5)) * 100)))
    labels = [(20, "Very Weak"), (40, "Weak"), (60, "Moderate"), (80, "Strong")]
    label = next((l for s, l in labels if score < s), "Very Strong")
    return score, label

def extract_features(url):
    try:
        parsed = urllib.parse.urlparse(url if '://' in url else 'http://' + url)
        domain, full = parsed.netloc.lower(), url.lower()
        
        feats = {
            'index': 1,
            'having_IPhaving_IP_Address': -1 if re.match(r'\d+\.\d+\.\d+\.\d+', domain) else 1,
            'URLURL_Length': 1 if len(full) < 54 else 0 if len(full) < 75 else -1,
            'Shortining_Service': -1 if any(s in full for s in ['bit.ly','goo.gl','t.co']) else 1,
            'having_At_Symbol': -1 if '@' in full else 1,
            'double_slash_redirecting': -1 if full.find('//') > 7 else 1,
            'Prefix_Suffix': -1 if '-' in domain else 1,
            'having_Sub_Domain': 1 if domain.count('.') == 1 else 0 if domain.count('.') == 2 else -1,
            'SSLfinal_State': 1 if full.startswith('https') else -1,
            'Domain_registeration_length': 1, 'Favicon': 1,
            'port': -1 if any(p in full for p in [':21',':22',':80']) else 1,
            'HTTPS_token': -1 if 'https' in domain else 1,
            'Request_URL': 1, 'URL_of_Anchor': 0, 'Links_in_tags': 0, 'SFH': 1,
            'Submitting_to_email': -1 if 'mailto:' in full else 1,
            'Abnormal_URL': 1 if domain in full else -1,
            'Redirect': -1 if full.count('//') > 1 else 1,
            'on_mouseover': 1, 'RightClick': 1, 'popUpWidnow': 1, 'Iframe': 1,
            'age_of_domain': 0, 'DNSRecord': 1, 'web_traffic': 0, 'Page_Rank': 0,
            'Google_Index': 1, 'Links_pointing_to_page': 0,
            'Statistical_report': -1 if any(b in domain for b in ['phish','scam']) else 1,
        }
        return pd.DataFrame([feats])[SVM_FEATURES]
    except: return None

def predict_url(url):
    features = extract_features(url)
    if features is None: return "invalid", "Unknown", 0

    scaled = svm_scaler.transform(features)
    prediction = svm_model.predict(scaled)[0]
    
    try:
        probabilities = svm_model.predict_proba(scaled)[0]
        confidence = round(np.max(probabilities) * 100)
    except AttributeError:
        decision = svm_model.decision_function(scaled)[0]
        confidence = round(100 / (1 + np.exp(-abs(decision))))

    # --- THRESHOLD LOGIC ---
    if confidence <= 50: # Increased from 30
        res, status = "phishing", "Phishing"
    elif 51 <= confidence <= 70:
        res, status = "phishing", "Risky"
    elif 71 <= confidence <= 85: # Now 80% will show as Vulnerable
        res, status = "legit", "Vulnerable"
    else:
        res, status = "legit", "Safe"

    # Final override if model is certain it's a threat
    if prediction == -1 and confidence > 75: status = "Risky"

    return res, status, confidence

# ╔══════════════════════════════════════════════════════╗
# ║  ROUTES                                              ║
# ╚══════════════════════════════════════════════════════╝

@app.route('/score', methods=['POST'])
def score_route():
    data = request.get_json()
    s, l = score_password(data.get('password', ''))
    return jsonify({'score': s, 'label': l})

@app.route('/check_phishing', methods=['POST'])
@app.route('/check_url', methods=['POST'])
def analysis_route():
    data = request.get_json()
    res, status, conf = predict_url(data.get('url', ''))
    return jsonify({'result': res, 'status': status, 'confidence': conf})

if __name__ == '__main__':
    print("🚀 SpectroGuard Final Backend Active on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
