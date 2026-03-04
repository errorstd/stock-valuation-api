# Pydantic models for the API

from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List

class CompanyBase(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[int] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[int] = None

class Company(CompanyBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ESGScoreBase(BaseModel):
    environmental_score: Optional[float]
    social_score: Optional[float]
    governance_score: Optional[float]
    total_esg_score: Optional[float]
    carbon_intensity: Optional[float]
    controversy_score: Optional[float]
    date: date

class CompanyDetail(Company):
    esg_scores: List[ESGScoreBase] = []
    
    class Config:
        orm_mode = True
