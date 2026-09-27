# 🧅 OnionVision AI (OnionGrade.Ai)

> **State-of-the-Art Intelligent Onion Quality Grading, Disease Detection & Mandi Market Valuation System**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![YOLOv11](https://img.shields.io/badge/YOLO-v11-00FFFF.svg)](https://github.com/ultralytics/ultralytics)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 🌟 Overview

**OnionVision AI** is an advanced computer vision and deep learning platform engineered for farmers, traders, agricultural aggregators, and Mandi market inspectors. It performs automated single and multi-onion bulb segmentation, 4-class quality classification (Healthy, Damaged, Rotten, Sprouted), AGMARK standard sizing & grading, voice narration, and live market valuation.

---

## ✨ Key Features

- 🎯 **Advanced YOLOv11 Classification & Segmentation**:
  - Trained on 1,188+ verified onion bulb samples with 93.9%+ validation accuracy.
  - Custom calibrated HSV/LAB color masking + distance transform peak isolation to accurately separate clustered onions and reject complex patterned backgrounds (bedsheets, sacks, tables).
- 📸 **Live Camera HUD & Bulk Upload**:
  - Interactive camera stream with 3-second snapshot countdown and front/rear camera switcher.
  - Multi-image drag-and-drop batch processing for large farm lots.
- 📊 **Commercial AGMARK Grading & Mandi Valuation**:
  - Automatically categorizes batches into **Grade A (Premium)**, **Grade B (Commercial)**, and **Grade C (Cull/Reject)**.
  - Real-time Mandi market revenue estimator with live price adjustments (₹/Quintal).
- 🔊 **Voice Assistant Narration (TTS)**:
  - Audio summary reading lot health score, bulb counts, and market recommendations.
- 📄 **Exportable Reports**:
  - One-click PDF Inspection Certificates and CSV data exports.
- 💎 **Modern Glassmorphic UI**:
  - Ultra-sleek dark/light theme, responsive dashboard with Chart.js analytics, lot history search, and filter capabilities.

---

## 📁 Project Architecture

```
OnionGrade AI/
├── app.py                      # Application factory & server entrypoint
├── config.py                   # App configurations & grading thresholds
├── requirements.txt            # Python dependencies
├── Procfile                    # Production deployment config (Render / Heroku)
├── render.yaml                 # Infrastructure configuration
│
├── database/                   # SQLite database models & query helpers
│   ├── db.py
│   └── models.py
│
├── models/                     # Deep learning weights & model descriptors
│   ├── best.pt                 # YOLOv11 trained classifier
│   └── README.md
│
├── routes/                     # Application Blueprints
│   ├── api.py                  # RESTful API endpoints (/api/analyze, /api/history)
│   └── pages.py                # Web view route controllers
│
├── services/                   # Core business & CV logic
│   ├── detection_service.py    # HSV/LAB segmentation & YOLO inference
│   ├── grading_service.py      # AGMARK standards & Mandi valuation
│   └── report_service.py       # PDF/CSV report generation
│
├── static/                     # CSS styling, JavaScript modules & assets
│   ├── css/style.css
│   ├── js/inspection.js
│   ├── js/main.js
│   └── demo/
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── inspect.html
│   ├── results.html
│   ├── dashboard.html
│   ├── history.html
│   ├── about.html
│   └── 404.html / 500.html
│
├── tests/                      # Automated test suite
│   └── test_api.py
│
└── training/                   # Dataset preprocessing & training scripts
    ├── data.yaml
    ├── merge_datasets.py
    └── prepare_cls_dataset.py
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/lohith012/OnionGrade.Ai.git
cd OnionGrade.Ai
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your web browser.

---

## 🧪 Testing

Run the automated test suite:
```bash
pytest tests/
```

---

## 🏷️ Quality Classification Classes

| Class | Description | Recommended Market Action |
|---|---|---|
| **Healthy** | Firm outer skin, vibrant coloration, zero rot or sprouts | Premium Fresh Market (Grade A) |
| **Damaged** | Surface cuts, peeled outer scales, minor bruising | Immediate Local Sale / Processing (Grade B) |
| **Sprouted** | Internal/external vegetative sprout emerging from neck | Urgent Dehydration / Processing |
| **Rotten** | Fungal decay, bacterial soft rot, mold | Discard / Compost (Grade C) |

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.