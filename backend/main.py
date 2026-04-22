from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
import pickle
import io
import os

from database import engine, Base, get_db
from models import UploadedDataset, BiasReport
from bias_detector import run_bias_analysis
from explainer import get_shap_explanation
from fastapi.responses import StreamingResponse
import io
from report_generator import generate_bias_report_pdf
# ── Create Tables ────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FairScan API")

# ── CORS (allows React frontend to talk to backend) ──────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ── 1. Root ──────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "FairScan API is running"}

# ── 2. Upload Dataset ────────────────────────────────────────────
@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    # Save record to DB
    record = UploadedDataset(
        filename=file.filename,
        row_count=len(df),
        column_count=len(df.columns),
        sensitive_attributes="gender,race"
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "File uploaded successfully",
        "dataset_id": record.id,
        "filename": file.filename,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist()
    }

# ── 3. Run Bias Analysis ─────────────────────────────────────────
@app.get("/analyze/{dataset_id}")
def analyze_bias(dataset_id: int, sensitive_col: str = "gender", db: Session = Depends(get_db)):
    dataset = db.query(UploadedDataset).filter(UploadedDataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Run bias analysis
    report = run_bias_analysis(sensitive_col)

    # Save report to DB
    bias_record = BiasReport(
        dataset_id=dataset_id,
        disparate_impact_score=report["disparate_impact_score"],
        statistical_parity_score=report["statistical_parity_score"],
        equal_opportunity_score=report["equal_opportunity_score"],
        overall_bias_level=report["overall_bias_level"],
        recommendations=report["recommendations"]
    )
    db.add(bias_record)
    db.commit()
    db.refresh(bias_record)

    return {
        "report_id": bias_record.id,
        "dataset_id": dataset_id,
        "sensitive_attribute": sensitive_col,
        "group_positive_rates": report["group_positive_rates"],
        "disparate_impact_score": report["disparate_impact_score"],
        "statistical_parity_score": report["statistical_parity_score"],
        "equal_opportunity_score": report["equal_opportunity_score"],
        "tpr_by_group": report["tpr_by_group"],
        "overall_bias_level": report["overall_bias_level"],
        "recommendations": report["recommendations"]
    }

# ── 4. Get SHAP Explanation ──────────────────────────────────────
@app.get("/explain")
def explain():
    result = get_shap_explanation(sample_size=100)
    return result

# ── 5. Get All Reports ───────────────────────────────────────────
@app.get("/reports")
def get_all_reports(db: Session = Depends(get_db)):
    reports = db.query(BiasReport).all()
    return [
        {
            "report_id": r.id,
            "dataset_id": r.dataset_id,
            "overall_bias_level": r.overall_bias_level,
            "disparate_impact_score": r.disparate_impact_score,
            "statistical_parity_score": r.statistical_parity_score,
            "equal_opportunity_score": r.equal_opportunity_score,
            "recommendations": r.recommendations,
            "created_at": str(r.created_at)
        }
        for r in reports
    ]

# ── 6. Get Single Report ─────────────────────────────────────────
@app.get("/reports/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(BiasReport).filter(BiasReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "report_id": report.id,
        "dataset_id": report.dataset_id,
        "overall_bias_level": report.overall_bias_level,
        "disparate_impact_score": report.disparate_impact_score,
        "statistical_parity_score": report.statistical_parity_score,
        "equal_opportunity_score": report.equal_opportunity_score,
        "recommendations": report.recommendations,
        "created_at": str(report.created_at)
    }

# ── 7. Download PDF Report ───────────────────────────────────────
@app.get("/reports/{report_id}/pdf")
def download_pdf(report_id: int, sensitive_col: str = "gender", db: Session = Depends(get_db)):
    report = db.query(BiasReport).filter(BiasReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Re-run bias analysis to get group rates
    bias_data = run_bias_analysis(sensitive_col)

    report_dict = {
        "report_id": report.id,
        "dataset_id": report.dataset_id,
        "sensitive_attribute": sensitive_col,
        "disparate_impact_score": report.disparate_impact_score,
        "statistical_parity_score": report.statistical_parity_score,
        "equal_opportunity_score": report.equal_opportunity_score,
        "overall_bias_level": report.overall_bias_level,
        "recommendations": report.recommendations,
        "group_positive_rates": bias_data["group_positive_rates"]
    }

    pdf_bytes = generate_bias_report_pdf(report_dict)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=fairscan_report_{report_id}.pdf"}
    )