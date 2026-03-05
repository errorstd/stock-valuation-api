"""
FastAPI Main Application
ESG Investment Insight KPI API
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import date, timedelta

from app.database import get_db
from app import models, schemas

# Create FastAPI app
app = FastAPI(
    title="ESG Investment Insight KPI API",
    description="Data-driven API for ESG metrics and investment analytics",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc UI
)

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/", tags=["Health"])
def root():
    """API Health Check"""
    return {
        "message": "ESG Investment Insight API",
        "status": "running",
        "docs": "/docs",
        "version": "1.0.0"
    }

# ============================================================================
# COMPANIES CRUD ENDPOINTS
# ============================================================================

@app.post("/companies/", response_model=schemas.Company, tags=["Companies"])
def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    """Create a new company"""
    # Check if company already exists
    existing = db.query(models.Company).filter(
        models.Company.symbol == company.symbol
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Company {company.symbol} already exists")
    
    db_company = models.Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@app.get("/companies/", response_model=List[schemas.Company], tags=["Companies"])
def get_companies(
    skip: int = 0,
    limit: int = 100,
    sector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of all companies"""
    query = db.query(models.Company)
    
    if sector:
        query = query.filter(models.Company.sector == sector)
    
    companies = query.offset(skip).limit(limit).all()
    return companies

@app.get("/companies/{symbol}", response_model=schemas.CompanyDetail, tags=["Companies"])
def get_company(symbol: str, db: Session = Depends(get_db)):
    """Get detailed information for a specific company"""
    company = db.query(models.Company).filter(
        models.Company.symbol == symbol.upper()
    ).first()
    
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {symbol} not found")
    
    return company

@app.put("/companies/{symbol}", response_model=schemas.Company, tags=["Companies"])
def update_company(
    symbol: str,
    company_update: schemas.CompanyUpdate,
    db: Session = Depends(get_db)
):
    """Update company information"""
    db_company = db.query(models.Company).filter(
        models.Company.symbol == symbol.upper()
    ).first()
    
    if not db_company:
        raise HTTPException(status_code=404, detail=f"Company {symbol} not found")
    
    # Update only provided fields
    for key, value in company_update.dict(exclude_unset=True).items():
        setattr(db_company, key, value)
    
    db.commit()
    db.refresh(db_company)
    return db_company

@app.delete("/companies/{symbol}", tags=["Companies"])
def delete_company(symbol: str, db: Session = Depends(get_db)):
    """Delete a company"""
    db_company = db.query(models.Company).filter(
        models.Company.symbol == symbol.upper()
    ).first()
    
    if not db_company:
        raise HTTPException(status_code=404, detail=f"Company {symbol} not found")
    
    db.delete(db_company)
    db.commit()
    
    return {"message": f"Company {symbol} deleted successfully"}

# ============================================================================
# ANALYTICS & KPI ENDPOINTS (This is where you STAND OUT!)
# ============================================================================

@app.get("/analytics/portfolio/average-esg", tags=["Analytics"])
def get_portfolio_average_esg(
    symbols: str = Query(..., description="Comma-separated company symbols, e.g., AAPL,MSFT,GOOGL"),
    db: Session = Depends(get_db)
):
    """
    Calculate portfolio-weighted average ESG score
    
    Example: /analytics/portfolio/average-esg?symbols=AAPL,MSFT,GOOGL
    """
    symbol_list = [s.strip().upper() for s in symbols.split(',')]
    
    # Get latest ESG scores with market cap
    results = db.query(
        models.Company.symbol,
        models.Company.name,
        models.Company.market_cap,
        models.ESGScore.total_esg_score
    ).join(models.ESGScore).filter(
        models.Company.symbol.in_(symbol_list)
    ).all()
    
    if not results:
        raise HTTPException(status_code=404, detail="No ESG data found for provided symbols")
    
    # Calculate weighted average
    total_market_cap = sum(r.market_cap for r in results if r.market_cap)
    
    if total_market_cap == 0:
        raise HTTPException(status_code=400, detail="Invalid market cap data")
    
    weighted_score = sum(
        (r.total_esg_score or 0) * (r.market_cap / total_market_cap)
        for r in results if r.total_esg_score and r.market_cap
    )
    
    return {
        "portfolio_symbols": symbol_list,
        "average_esg_score": round(weighted_score, 2),
        "total_market_cap": total_market_cap,
        "num_companies": len(results),
        "companies": [
            {
                "symbol": r.symbol,
                "name": r.name,
                "esg_score": r.total_esg_score,
                "weight": round((r.market_cap / total_market_cap) * 100, 2)
            }
            for r in results
        ]
    }

@app.get("/analytics/top-performers", tags=["Analytics"])
def get_top_esg_performers(
    limit: int = Query(10, description="Number of companies to return"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    db: Session = Depends(get_db)
):
    """Get top ESG performing companies"""
    query = db.query(
        models.Company.symbol,
        models.Company.name,
        models.Company.sector,
        models.ESGScore.total_esg_score,
        models.ESGScore.environmental_score,
        models.ESGScore.social_score,
        models.ESGScore.governance_score
    ).join(models.ESGScore).filter(
        models.ESGScore.total_esg_score.isnot(None)
    )
    
    if sector:
        query = query.filter(models.Company.sector == sector)
    
    results = query.order_by(desc(models.ESGScore.total_esg_score)).limit(limit).all()
    
    return {
        "filter": {"sector": sector, "limit": limit},
        "top_performers": [
            {
                "rank": idx + 1,
                "symbol": r.symbol,
                "name": r.name,
                "sector": r.sector,
                "total_esg_score": r.total_esg_score,
                "environmental_score": r.environmental_score,
                "social_score": r.social_score,
                "governance_score": r.governance_score
            }
            for idx, r in enumerate(results)
        ]
    }

@app.get("/analytics/sector-distribution", tags=["Analytics"])
def get_sector_esg_distribution(db: Session = Depends(get_db)):
    """Get average ESG scores by sector"""
    results = db.query(
        models.Company.sector,
        func.avg(models.ESGScore.total_esg_score).label('avg_esg'),
        func.avg(models.ESGScore.environmental_score).label('avg_environmental'),
        func.avg(models.ESGScore.social_score).label('avg_social'),
        func.avg(models.ESGScore.governance_score).label('avg_governance'),
        func.count(models.Company.id).label('company_count')
    ).join(models.ESGScore).group_by(models.Company.sector).all()
    
    return {
        "sectors": [
            {
                "sector": r.sector,
                "average_esg_score": round(r.avg_esg, 2),
                "average_environmental": round(r.avg_environmental, 2),
                "average_social": round(r.avg_social, 2),
                "average_governance": round(r.avg_governance, 2),
                "num_companies": r.company_count
            }
            for r in results
        ]
    }

@app.get("/analytics/risk-flags", tags=["Analytics"])
def get_risk_flags(
    controversy_threshold: float = Query(5.0, description="Controversy score threshold"),
    db: Session = Depends(get_db)
):
    """Identify companies with ESG risk flags"""
    results = db.query(
        models.Company.symbol,
        models.Company.name,
        models.Company.sector,
        models.ESGScore.controversy_score,
        models.ESGScore.total_esg_score
    ).join(models.ESGScore).filter(
        models.ESGScore.controversy_score >= controversy_threshold
    ).order_by(desc(models.ESGScore.controversy_score)).all()
    
    return {
        "threshold": controversy_threshold,
        "high_risk_companies": [
            {
                "symbol": r.symbol,
                "name": r.name,
                "sector": r.sector,
                "controversy_score": r.controversy_score,
                "esg_score": r.total_esg_score,
                "risk_level": "High" if r.controversy_score >= 7 else "Medium"
            }
            for r in results
        ],
        "total_flagged": len(results)
    }

# ============================================================================
# SECTORS ENDPOINT
# ============================================================================

@app.get("/sectors/", tags=["Sectors"])
def get_sectors(db: Session = Depends(get_db)):
    """Get list of all available sectors"""
    sectors = db.query(models.Company.sector).distinct().all()
    return {
        "sectors": [s[0] for s in sectors if s[0]]
    }
