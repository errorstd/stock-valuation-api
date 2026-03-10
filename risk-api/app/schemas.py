"""
Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional, List


# ============================================================================
# COMPANY SCHEMAS
# ============================================================================

class CompanyBase(BaseModel):
    """Base company schema with common fields"""
    symbol: str = Field(..., max_length=10, description="Stock ticker symbol")
    name: str = Field(..., max_length=255, description="Company name")
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    marketcap: Optional[int] = Field(None, description="Market cap in USD")
    
    @field_validator('symbol')
    @classmethod
    def uppercase_symbol(cls, v):
        """Automatically uppercase symbol"""
        return v.upper() if v else v


class CompanyCreate(CompanyBase):
    """Schema for creating a new company"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "NVDA",
                "name": "NVIDIA Corporation",
                "sector": "Technology",
                "industry": "Semiconductors",
                "marketcap": 2200000000000
            }
        }


class CompanyUpdate(BaseModel):
    """Schema for updating company info"""
    name: Optional[str] = Field(None, max_length=255)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    marketcap: Optional[int] = None


class Company(CompanyBase):
    """Full company schema with database fields"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# FINANCIAL METRIC SCHEMAS
# ============================================================================

class FinancialMetricBase(BaseModel):
    """Base financial metric schema"""
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    revenue: Optional[int] = None
    profit_margin: Optional[float] = None
    debt_to_equity: Optional[float] = None
    date: date


class FinancialMetricResponse(FinancialMetricBase):
    """Financial metric response with ID"""
    id: int
    company_id: int
    
    class Config:
        from_attributes = True


# ============================================================================
# STOCK PRICE SCHEMAS
# ============================================================================

class StockPriceBase(BaseModel):
    """Base stock price schema"""
    date: date
    open: float
    close: float
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[int] = None


class StockPriceResponse(StockPriceBase):
    """Stock price response with ID"""
    id: int
    company_id: int
    
    class Config:
        from_attributes = True


# ============================================================================
# DETAILED RESPONSE SCHEMAS
# ============================================================================

class CompanyDetail(Company):
    """Detailed company info with related data"""
    financial_metrics: List[FinancialMetricResponse] = []
    stock_prices: List[StockPriceResponse] = []
    
    class Config:
        from_attributes = True
