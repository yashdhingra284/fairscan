# FairScan — AI Bias Auditor

> Detect & Fix AI Bias Before It Harms People

Built for **Hack2Skill Solution Challenge 2026** under the **Unbiased AI Decision** track.

## What is FairScan?
FairScan is a web application that allows organizations to upload hiring datasets, automatically detect bias against demographic groups (gender, race, age), and receive actionable fix suggestions.

## Features
- Upload any CSV dataset for bias analysis
- Detects bias using 3 industry-standard metrics:
  - Disparate Impact
  - Statistical Parity
  - Equal Opportunity
- Gender and Race bias analysis
- SHAP explainability — shows WHY the model is biased
- Downloadable PDF fairness report
- Dashboard with all past reports

## Tech Stack
### Backend
- FastAPI
- scikit-learn (Random Forest)
- AI Fairness 360 (AIF360)
- Fairlearn
- SHAP
- SQLAlchemy + SQLite
- ReportLab (PDF generation)

### Frontend
- React + TypeScript
- TanStack Router
- Tailwind CSS
- Axios

## Project Structure
fairscan/
├── backend/
│   ├── main.py
│   ├── bias_detector.py
│   ├── model_trainer.py
│   ├── explainer.py
│   ├── report_generator.py
│   ├── database.py
│   ├── models.py
│   └── requirements.txt
└── frontend/
└── src/
└── routes/
├── index.tsx
├── upload.tsx
├── analysis.tsx
└── dashboard.tsx

## Setup Instructions

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python model_trainer.py
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Dataset
Uses the [Adult Income Dataset](https://archive.ics.uci.edu/ml/datasets/adult) from UCI ML Repository.
Place `adult.csv` in the `backend/` folder before running.

## Results
The model detects **significant bias**:
- Gender: Disparate Impact = 0.36 (threshold ≥ 0.8)
- Race: Disparate Impact = 0.30 (threshold ≥ 0.8)