from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class UploadedDataset(Base):
    __tablename__ = "uploaded_datasets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())
    row_count = Column(Integer)
    column_count = Column(Integer)
    sensitive_attributes = Column(String)

class BiasReport(Base):
    __tablename__ = "bias_reports"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    disparate_impact_score = Column(Float)
    statistical_parity_score = Column(Float)
    equal_opportunity_score = Column(Float)
    overall_bias_level = Column(String)
    recommendations = Column(Text)