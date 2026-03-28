<div align="center">

# 🛡️ SpectroGuard
### AI-Powered Cybersecurity Toolkit

> 💡 *"Cyber threats change daily — so we built a system that adapts, not one that depends on a static database."*

</div>

---

## 📌 Overview

**SpectroGuard** is a Flask-powered web application that brings **4 AI-backed cybersecurity tools** together in one simple interface. It was built to make cybersecurity **accessible, educational, and practical** for everyday users — no technical knowledge required.

Instead of using multiple websites or tools, SpectroGuard provides all essential security features in **one platform with a single click**.

---

## 🔧 Tools & Algorithms

### 🔑 1. Password Strength Checker
> **Algorithm:** Higher-Order Markov Model

Analyzes password strength by evaluating character patterns and sequence probability — far more accurate than simple rule-based checkers.

- ✅ Learns patterns from large password datasets
- 🔴 Common patterns → **Weak** &nbsp;|&nbsp; 🟢 Rare sequences → **Strong**
- ✅ More accurate than rule-based checkers

---

### 🌐 2. Phishing Website Detector
> **Algorithm:** SVM (Support Vector Machine) Classifier

Detects fake/scam websites using a trained machine learning model.

| Feature Checked | Description |

| URL Length | Unusually long URLs are flagged |
| HTTPS Presence | Missing HTTPS is a red flag |
| Suspicious Keywords | `login`, `verify`, `account-update` etc. |
| Domain Age | Newly registered domains flagged |

- 🟢 **Safe** or 🔴 **Phishing** — clear classification output

---

### 🔗 3. Phishing URL Detector
> **Algorithm:** 3-Layer Detection System

Uses a three-layer detection approach for maximum accuracy:

```
🚫 Layer 1 — Blacklist      → Known malicious URLs automatically blocked
✅ Layer 2 — Whitelist      → Trusted domains automatically allowed
🔍 Layer 3 — Heuristic      → Pattern-based detection for unknown URLs
```

**Heuristic checks include:**
- Suspicious words: `login`, `verify`, `account-update`
- URL too long or structurally abnormal
- Domain typos or weird subdomains
- No HTTPS, random character strings

---

### #️⃣ 4. Hash ID Generator
> **Algorithm:** SHA-256

Converts any input into a fixed-length **256-bit hash**.

- 🔒 One-way hashing — original input **cannot** be recovered
- ⚡ Implemented client-side in JavaScript (no server dependency)
- ✅ More secure than MD5 or SHA-1

---

### 📊 5. Algorithm Analysis Tab

Compares SpectroGuard's algorithms against standard alternatives. Generates scores for:

| Metric | Description |
|---|---|
| ⚡ Computational Efficiency | Speed of processing |
| 🧠 Memory Usage | RAM consumption |
| 📉 Log Likelihood | Statistical accuracy |

---

## 📁 Project Structure

```
SpectroGuard-BE-Project/
├── Data/               ← Training datasets for ML models
├── Models/             ← Trained SVM and Markov Model files
├── Scripts/            ← Python backend scripts
├── Web/                ← Frontend (HTML, JS) + Flask app
│   ├── app.py          ← Main Flask application
│   └── Index.html      ← Main webpage
└── README.md
```

---

## 🚀 How to Run

### 🪟 Windows

```bash
# First time only
cd "path/to/SpectroGuard-BE-Project/Web"
python -m venv venv
venv\Scripts\activate
pip install flask flask-cors scikit-learn pandas numpy

# Every time after that
venv\Scripts\activate
python app.py
# Then open Index.html in your browser
```

### 🐧 Linux / Kali

```bash
# First time only
cd "path/to/SpectroGuard-BE-Project/Web"
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors scikit-learn pandas numpy

# Every time after that
source venv/bin/activate
python3 app.py
# Then open Index.html in your browser
```

> ⚠️ **Keep the terminal open while using the website.**

---

## 🔭 Future Scope

| Feature | Description |

| 🧩 Browser Extension | Real-time link safety warnings before clicking |
| 💬 Live Password Scoring | Suggest strong passwords as users type online |

---

## 🧑‍💻 Team

| Name | Role |

| **Pratiksha Alhat** | Project Leader · Testing · Integration · Backend |
| **Shraddha Gadekar** | Frontend (UI/UX) · Documentation · Module Development |
| **Kapil Waghumbare** | Frontend (UI/UX) · Module Development · Backend |
| **Dr. Swapnil S. Chaudhari** | Project Guide |

🏫 **Marathwada Mitra Mandal's Institute of Technology, Pune (SPPU)**

---

## 🔗 Connect

**Pratiksha Alhat**
[LinkedIn](https://www.linkedin.com/in/pratiksha-alhat-305aaa265/)
[GitHub](https://github.com/Pratu0405-a)

**Kapil Waghumbare**
[LinkedIn](https://www.linkedin.com/in/kapil-waghumbare-5421b4293)
[GitHub](https://github.com/Kapil-Waghumbare)

**Shraddha Gadekar**
[LinkedIn](https://www.linkedin.com/in/shraddha-gadekar-7a6b24259/)
[GitHub](https://github.com/ShraddhaG-01)

---

## 📄 License

This project was developed for educational purposes as part of a Final Year BE Project.

© 2025 SpectroGuard Team — MMIT Pune
