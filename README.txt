# SpectroGuard — Cybersecurity Toolkit

> A web-based cybersecurity toolkit built for non-technical users.  
> Final Year BE Project | MMIT Pune | 2025

---

## Overview

SpectroGuard is a Flask-powered web application that brings 4 AI-backed 
cybersecurity tools together in one simple interface. It was built to make 
cybersecurity accessible to everyday users — no technical knowledge required.

**Tech Stack:** Python  •  Flask  •  Scikit-learn  •  JavaScript  •  HTML · Scikit-learn · SVM · Markov Model

---

## Tools

### 1. Password Strength Checker
Analyzes password strength using a **Higher Order Markov Model** that 
evaluates character patterns and sequence probability — more accurate 
than simple rule-based checkers.

### 2. Hash ID Generator
Generates a secure hash of any input using the **SHA-256 algorithm**, 
implemented directly in JavaScript on the client side for fast, 
secure hashing without server dependency.

### 3. URL Legitimacy Checker
Scans any URL using a combination of:
- **Blacklist** — known malicious URLs
- **Whitelist** — trusted domains
- **Heuristic Analysis** — pattern-based detection of suspicious URLs

### 4. Phishing Website Detector
Uses a trained **SVM (Support Vector Machine)** classifier to detect 
phishing websites based on URL and website features.

### 5. Algorithm Analysis Tab
Compares our implemented algorithms against standard alternatives on 
real user input. Generates scores for:
- Computational Efficiency
- Memory Usage
- Log Likelihood

---

## Project Structure
```
SpectroGuard-BE-Project/
├── Data/          — Training datasets for ML models
├── Models/        — Trained SVM and Markov Model files
├── Scripts/       — Python backend scripts
├── Web/           — Frontend (HTML, JS) + Flask app
│   ├── app.py     — Main Flask application
│   └── Index.html — Main webpage
└── README.md
```

---

## How to Run

### Windows
```bash
# First time only
cd "path/to/SpectroGuard-BE-Project/Web"
python -m venv venv
venv\Scripts\activate
pip install flask flask-cors scikit-learn pandas numpy

# Every time
venv\Scripts\activate
python app.py
# Then open Index.html in browser
```

### Linux / Kali
```bash
# First time only
cd "path/to/SpectroGuard-BE-Project/Web"
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors scikit-learn pandas numpy

# Every time
source venv/bin/activate
python app.py
# Then open Index.html in browser
```

> **Note:** Keep the terminal open while using the website.

---

## Team

Built by a 3-member team as part of the Final Year BE Project at  
**Marathwada Mitra Mandal's Institute of Technology, Pune (SPPU)**

---

## Connect

**Kapil Waghumbare**  
[LinkedIn](https://www.linkedin.com/in/kapil-waghumbare-5421b4293) · 
[GitHub](https://github.com/Kapil-Waghumbare)
