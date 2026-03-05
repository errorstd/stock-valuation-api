"""
SQLAlchemy Database Models
Defines the structure of all database tables
"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Company(Base):
    """Company information table"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    esg_scores = relationship("ESGScore", back_populates="company", cascade="all, delete-orphan")
    financial_metrics = relationship("FinancialMetric", back_populates="company", cascade="all, delete-orphan")
    stock_prices = relationship("StockPrice", back_populates="company", cascade="all, delete-orphan")

class ESGScore(Base):
    """ESG scores and sustainability metrics"""
    __tablename__ = "esg_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    environmental_score = Column(Float)
    social_score = Column(Float)
    governance_score = Column(Float)
    total_esg_score = Column(Float, index=True)
    carbon_intensity = Column(Float)
    controversy_score = Column(Float)
    date = Column(Date, nullable=False, index=True)
    
    # Relationship
    company = relationship("Company", back_populates="esg_scores")

class FinancialMetric(Base):
    """Financial performance metrics"""
    __tablename__ = "financial_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    pe_ratio = Column(Float)
    eps = Column(Float)
    revenue = Column(BigInteger)
    profit_margin = Column(Float)
    debt_to_equity = Column(Float)
    date = Column(Date, nullable=False, index=True)
    
    # Relationship
    company = relationship("Company", back_populates="financial_metrics")

class StockPrice(Base):
    """Historical stock price data"""
    __tablename__ = "stock_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    
    # Relationship
    company = relationship("Company", back_populates="stock_prices")
