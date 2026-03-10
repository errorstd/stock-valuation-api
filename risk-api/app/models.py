"""
SQLAlchemy Database Models
"""

from sqlalchemy import Column, Integer, String, Float, BigInteger, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Company(Base):
    """Company model - stores basic company information"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    
    # ✅ FIX: Use 'marketcap' (no underscore)
    marketcap = Column(BigInteger, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships with CASCADE DELETE
    financial_metrics = relationship(
        "FinancialMetric",
        back_populates="company",
        cascade="all, delete-orphan"
    )
    
    stock_prices = relationship(
        "StockPrice",
        back_populates="company",
        cascade="all, delete-orphan"
    )


class FinancialMetric(Base):
    """Financial metrics - P/E ratio, EPS, margins, etc."""
    __tablename__ = "financial_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    pe_ratio = Column(Float, nullable=True)
    eps = Column(Float, nullable=True)
    revenue = Column(BigInteger, nullable=True)
    profit_margin = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    
    date = Column(Date, nullable=False)
    
    # Relationship
    company = relationship("Company", back_populates="financial_metrics")


class StockPrice(Base):
    """Stock price history"""
    __tablename__ = "stock_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=True)
    
    # Relationship
    company = relationship("Company", back_populates="stock_prices")
