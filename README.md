<p align="center">
  <img src="https://github.com/user-attachments/assets/bbd4cc2b-26f0-4cc4-9271-2f719e488dd4" width="1000" />
</p>
⭐ AstraScan – AI-Powered Web Vulnerability Scanner

Advanced Recon • AI Ranking • Parameter Discovery • Optional Active Testing

AstraScan is a lightweight yet powerful AI-assisted web vulnerability scanner designed for reconnaissance, parameter discovery, and machine-learning-based risk scoring.

It does not exploit, attack, or bypass security systems.
It is built to be safe for learning and research.

---

📌 Features :

---

🔍 1. Smart Crawler

-  Extracts pages up to a configurable depth

-  Parses links, forms, parameters

Handles HTTPS, timeouts, redirects

Can run through Tor (optional)

Randomized headers for cleaner, more realistic crawling

🧠 2. AI-Assisted Risk Scoring

Generates feature vectors from URLs + HTML

ML model learns page patterns

Ranks pages by risk likelihood

Saves complete scoring JSON

📝 3. Parameter & Form Extraction

Detects GET parameters from URLs

Finds forms + input fields in HTML

Collects data for later active testing

⚔️ 4. Optional Active Tests

Only if user enables --active

Conservative XSS tests

Conservative SQLi tests

Logged safely to reports/ai_results.json
---

#🚀 Installation

git clone https://github.com/yourname/AstraScan
cd AstraScan , 
python3 -m venv venv , 
source venv/bin/activate , 
pip install -r requirements.txt


---

## 🎥 Demo Img

<p align="center">
  <img src="https://github.com/user-attachments/assets/bb3e03fa-61ce-4694-8c0d-c6d1c1bb7312" width="1000" />
</p>

---

