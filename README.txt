### 🛡️ SpectroGuard — AI-Powered Cybersecurity Toolkit
---

### 📌 Overview

**SpectroGuard** is a Flask-powered web application that brings **4 AI-backed cybersecurity tools** together in one simple interface. It was built to make cybersecurity **accessible, educational, and practical** for everyday users — no technical knowledge required.

Instead of using multiple websites or tools, SpectroGuard provides all essential security features in **one platform with a single click**.

> 💡 *"Cyber threats change daily — so we built a system that adapts, not one that depends on a static database."*

**Tech Stack:**  
`Python` • `Flask` • `Scikit-learn` • `SVM` • `Markov Model` • `JavaScript` • `HTML/CSS` • `SHA-256`

---

###🔧 Tools & Algorithms

### 🔑 1. Password Strength Checker
Analyzes password strength using a **Higher-Order Markov Model** that evaluates character patterns and sequence probability.

- Learns patterns from large password datasets
- Rare sequences → **Strong** | Common patterns → **Weak**
- More accurate than simple rule-based checkers

---

### 🌐 2. Phishing Website Detector
Detects fake/scam websites using a trained **SVM (Support Vector Machine)** classifier.

- Checks: URL length, HTTPS presence, suspicious keywords (`login`, `verify`, etc.), domain age
- Classifies websites as **Safe** or **Phishing**

---

### 🔗 3. Phishing URL Detector
Uses a **three-layer detection approach**:

🚫 Blacklist - Known malicious URLs → automatically blocked 
 ✅ Whitelist - Trusted domains → automatically allowed 
🔍 Heuristic Analysis - Pattern-based detection for unknown URLs 

**Heuristic checks include:**
- Suspicious words: `login`, `verify`, `account-update`
- URL too long or structurally abnormal
- Domain typos or weird subdomains
- No HTTPS, random character strings

---

### #️⃣ 4. Hash ID Generator
Converts any input into a fixed-length **256-bit hash** using **SHA-256**.
- One-way hashing — original input cannot be recovered
- Implemented client-side in JavaScript (no server dependency)
- More secure than MD5 or SHA-1

---

### 📊 5. Algorithm Analysis Tab
Compares our algorithms against standard alternatives. Generates scores for:
- ⚡ Computational Efficiency
- 🧠 Memory Usage
- 📉 Log Likelihood

---

## 📁 Project Structure
```
SpectroGuard-BE-Project/
├── Data/           — Training datasets for ML models
├── Models/         — Trained SVM and Markov Model files
├── Scripts/        — Python backend scripts
├── Web/            — Frontend (HTML, JS) + Flask app
│   ├── app.py      — Main Flask application
│   └── Index.html  — Main webpage
└── README.md
```

---

### 🚀 How to Run

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
python app.py
# Then open Index.html in your browser
```

> ⚠️ **Keep the terminal open while using the website.**

---


## Future Scope

- 🧩 Browser Extension — real-time link safety warnings before clicking
- 💬 Password scoring — suggest strong passwords while users type online
---

## 🧑‍💻 Team

| Name | Role |
|---|---|
| **Pratiksha Alhat** | Project Leader, Testing, Integration, Backend |
| **Shraddha Gadekar** | Frontend (UI/UX), Documentation, Module Development |
| **Kapil Waghumbare** | Frontend (UI/UX), Module Development, Backend |
| **Dr. Swapnil S. Chaudhari** | Project Guide |

🏫 Marathwada Mitra Mandal's Institute of Technology, Pune (SPPU)

---

### 🔗 Connect

**Pratiksha Alhat**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin)](https://www.linkedin.com/in/pratiksha-alhat-305aaa265/)
[![GitHub](https://img.shields.io/badge/GitHub-black?logo=github)](https://github.com/Pratu0405-a)

**Kapil Waghumbare**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin)](https://www.linkedin.com/in/kapil-waghumbare-5421b4293)
[![GitHub](https://img.shields.io/badge/GitHub-black?logo=github)](https://github.com/Kapil-Waghumbare)

**Shraddha Gadekar**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin)](https://www.linkedin.com/in/shraddha-gadekar-7a6b24259/)
[![GitHub](https://img.shields.io/badge/GitHub-black?logo=github)](https://github.com/ShraddhaG-01)

---

## 📄 License

This project was developed for educational purposes as part of a Final Year BE Project.  
© 2025 SpectroGuard Team — MMIT Pune
