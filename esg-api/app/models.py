"""
SQLAlchemy Database Models
Defines the structure of all database tables
"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.database import Base  # ✅ Import Base from database.py

class Company(Base):
    """Company information table"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    sector = Column(String)
    industry = Column(String)
    market_cap = Column(BigInteger)
    
    # CASCADE DELETE - when company is deleted, delete all related records
    esg_scores = relationship("ESGScore", back_populates="company", cascade="all, delete-orphan")
    financial_metrics = relationship("FinancialMetric", back_populates="company", cascade="all, delete-orphan")
    stock_prices = relationship("StockPrice", back_populates="company", cascade="all, delete-orphan")

class ESGScore(Base):
    """ESG scores and sustainability metrics"""
    __tablename__ = "esg_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    environmental_score = Column(Float)
    social_score = Column(Float)
    governance_score = Column(Float)
    total_esg_score = Column(Float)
    carbon_intensity = Column(Float)
    controversy_score = Column(Float)
    date = Column(Date, nullable=False)
    
    company = relationship("Company", back_populates="esg_scores")

class FinancialMetric(Base):
    """Financial performance metrics"""
    __tablename__ = "financial_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    pe_ratio = Column(Float)
    eps = Column(Float)
    revenue = Column(BigInteger)
    profit_margin = Column(Float)
    debt_to_equity = Column(Float)
    date = Column(Date, nullable=False)
    
    company = relationship("Company", back_populates="financial_metrics")

class StockPrice(Base):
    """Historical stock price data"""
    __tablename__ = "stock_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    
    company = relationship("Company", back_populates="stock_prices")
