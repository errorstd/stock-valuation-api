"""
FastAPI Main Application - COMPREHENSIVE VERSION
ESG Investment Insight KPI API
Version 2.0.0 - With merged endpoints and enhanced features
"""

from fastapi import FastAPI, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
import csv
import io
import yfinance as yf
import yesg
import numpy as np
from datetime import date, datetime
from requests.exceptions import HTTPError

from app.database import get_db
from app import models, schemas

# Create FastAPI app
app = FastAPI(
    title="ESG Investment Insight KPI API",
    description="Data-driven API for ESG metrics and investment analytics",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def convert_numpy_to_python(value):
    """Convert numpy types to Python native types"""
    if value is None:
        return None
    if isinstance(value, (np.integer, np.floating)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.item()
    return value

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
        "version": "2.0.0",
        "features": [
            "Merged company endpoints",
            "Bulk CSV upload",
            "Real-time data fetching",
            "ESG analytics",
            "Portfolio analysis",
            "Risk assessment"
        ]
    }

# ============================================================================
# COMPANIES CRUD ENDPOINTS (MERGED & ENHANCED)
# ============================================================================

@app.post("/companies/", tags=["Companies"])
async def create_companies(
    company: Optional[schemas.CompanyCreate] = None,
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    🔥 MERGED ENDPOINT: Create single company OR bulk upload from CSV
    
    **Usage Option 1 - Single Company:**
    Send JSON body:
    ```json
    {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "market_cap": 2800000000000
    }
    ```
    
    **Usage Option 2 - Bulk CSV Upload:**
    Upload CSV file with format:
    ```
    symbol,name,sector,industry,market_cap
    AAPL,Apple Inc.,Technology,Consumer Electronics,2800000000000
    MSFT,Microsoft Corp.,Technology,Software,2500000000000
    ```
    """
    
    # CSV BULK UPLOAD
    if file:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        try:
            contents = await file.read()
            csv_data = contents.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            
            imported = []
            errors = []
            
            for row in csv_reader:
                try:
                    existing = db.query(models.Company).filter(
                        models.Company.symbol == row['symbol'].upper()
                    ).first()
                    
                    if existing:
                        errors.append(f"{row['symbol']}: Already exists")
                        continue
                    
                    company_obj = models.Company(
                        symbol=row['symbol'].upper(),
                        name=row['name'],
                        sector=row.get('sector'),
                        industry=row.get('industry'),
                        market_cap=int(row.get('market_cap', 0)) if row.get('market_cap') else None
                    )
                    
                    db.add(company_obj)
                    imported.append(row['symbol'].upper())
                    
                except Exception as e:
                    errors.append(f"{row.get('symbol', 'Unknown')}: {str(e)}")
            
            db.commit()
            
            return {
                "mode": "bulk_upload",
                "message": "Bulk upload completed",
                "imported_count": len(imported),
                "imported_symbols": imported,
                "error_count": len(errors),
                "errors": errors if errors else None
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
    
    # SINGLE COMPANY CREATE
    elif company:
        existing = db.query(models.Company).filter(
            models.Company.symbol == company.symbol.upper()
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Company {company.symbol} already exists"
            )
        
        db_company = models.Company(
            symbol=company.symbol.upper(),
            name=company.name,
            sector=company.sector,
            industry=company.industry,
            market_cap=company.market_cap
        )
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        
        return {
            "mode": "single_create",
            "message": f"Company {company.symbol} created successfully",
            "company": {
                "id": db_company.id,
                "symbol": db_company.symbol,
                "name": db_company.name,
                "sector": db_company.sector,
                "industry": db_company.industry,
                "market_cap": db_company.market_cap
            }
        }
    
    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide either company JSON data or CSV file"
        )

@app.get("/companies/", tags=["Companies"])
def get_companies_or_company(
    symbol: Optional[str] = Query(None, description="Specific company symbol (optional)"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Max records to return"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    db: Session = Depends(get_db)
):
    """
    🔥 MERGED ENDPOINT: Get all companies OR specific company
    
    **Usage Examples:**
    - Get all: `/companies/`
    - Get specific: `/companies/?symbol=AAPL`
    - Filter by sector: `/companies/?sector=Technology`
    - Pagination: `/companies/?skip=10&limit=20`
    - Combined: `/companies/?sector=Finance&limit=5`
    """
    
    # GET SPECIFIC COMPANY
    if symbol:
        company = db.query(models.Company).filter(
            models.Company.symbol == symbol.upper()
        ).first()
        
        if not company:
            raise HTTPException(
                status_code=404,
                detail=f"Company {symbol} not found"
            )
        
        # Get latest ESG score if available
        latest_esg = db.query(models.ESGScore).filter(
            models.ESGScore.company_id == company.id
        ).order_by(desc(models.ESGScore.date)).first()
        
        # Get latest financial data
        latest_financial = db.query(models.FinancialMetric).filter(
            models.FinancialMetric.company_id == company.id
        ).order_by(desc(models.FinancialMetric.date)).first()
        
        return {
            "mode": "single",
            "company": {
                "id": company.id,
                "symbol": company.symbol,
                "name": company.name,
                "sector": company.sector,
                "industry": company.industry,
                "market_cap": company.market_cap,
                "latest_esg_score": latest_esg.total_esg_score if latest_esg else None,
                "latest_esg_date": latest_esg.date.isoformat() if latest_esg else None,
                "pe_ratio": latest_financial.pe_ratio if latest_financial else None,
                "eps": latest_financial.eps if latest_financial else None
            }
        }
    
    # GET ALL COMPANIES (with optional filters)
    query = db.query(models.Company)
    
    if sector:
        query = query.filter(models.Company.sector == sector)
    
    total = query.count()
    companies = query.offset(skip).limit(limit).all()
    
    return {
        "mode": "list",
        "total": total,
        "showing": len(companies),
        "skip": skip,
        "limit": limit,
        "filters": {
            "sector": sector
        },
        "companies": [
            {
                "id": c.id,
                "symbol": c.symbol,
                "name": c.name,
                "sector": c.sector,
                "industry": c.industry,
                "market_cap": c.market_cap
            }
            for c in companies
        ]
    }

@app.get("/companies/{symbol}/fetch-live-data", tags=["Companies"])
def fetch_live_data(symbol: str, db: Session = Depends(get_db)):
    """
    🔥 Fetch real-time ESG and financial data from Yahoo Finance
    
    **Features:**
    - Fetches fresh data directly from Yahoo Finance API
    - Updates database with latest information
    - Handles rate limiting gracefully
    - Provides estimates when real data unavailable
    - Converts numpy types properly
    
    **Example:** `/companies/AAPL/fetch-live-data`
    """
    
    symbol = symbol.upper()
    
    # Get or create company
    company = db.query(models.Company).filter(
        models.Company.symbol == symbol
    ).first()
    
    if not company:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            company = models.Company(
                symbol=symbol,
                name=info.get('longName', symbol),
                sector=info.get('sector', 'Unknown'),
                industry=info.get('industry', 'Unknown'),
                market_cap=convert_numpy_to_python(info.get('marketCap', 0))
            )
            
            db.add(company)
            db.commit()
            db.refresh(company)
            
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"Company {symbol} not found: {str(e)}"
            )
    
    # Fetch ESG data with rate limit handling
    esg_data_result = None
    try:
        esg_data = yesg.get_esg_full(symbol)
        
        if esg_data is not None and not esg_data.empty:
            total_score = convert_numpy_to_python(esg_data.get('Total-Score', [None])[0])
            env_score = convert_numpy_to_python(esg_data.get('E-Score', [None])[0])
            social_score = convert_numpy_to_python(esg_data.get('S-Score', [None])[0])
            gov_score = convert_numpy_to_python(esg_data.get('G-Score', [None])[0])
            controversy = convert_numpy_to_python(esg_data.get('Highest Controversy', [0])[0])
            
            esg_score = db.query(models.ESGScore).filter(
                models.ESGScore.company_id == company.id,
                models.ESGScore.date == date.today()
            ).first()
            
            if esg_score:
                esg_score.environmental_score = env_score
                esg_score.social_score = social_score
                esg_score.governance_score = gov_score
                esg_score.total_esg_score = total_score
                esg_score.controversy_score = controversy if controversy else 0.0
            else:
                esg_score = models.ESGScore(
                    company_id=company.id,
                    environmental_score=env_score,
                    social_score=social_score,
                    governance_score=gov_score,
                    total_esg_score=total_score,
                    carbon_intensity=None,
                    controversy_score=controversy if controversy else 0.0,
                    date=date.today()
                )
                db.add(esg_score)
            
            db.commit()
            
            esg_data_result = {
                "environmental_score": esg_score.environmental_score,
                "social_score": esg_score.social_score,
                "governance_score": esg_score.governance_score,
                "total_esg_score": esg_score.total_esg_score,
                "controversy_score": esg_score.controversy_score,
                "source": "Yahoo Finance (Real-time)",
                "data_quality": "actual"
            }
        else:
            # Use estimates when no data available
            esg_data_result = {
                "environmental_score": 55.0,
                "social_score": 58.0,
                "governance_score": 62.0,
                "total_esg_score": 58.0,
                "controversy_score": 2.0,
                "source": "Industry Average (Estimated)",
                "data_quality": "estimated",
                "note": "Real ESG data not available for this symbol"
            }
    
    except HTTPError as e:
        if e.response.status_code == 429:
            esg_data_result = {
                "error": "Rate limited by Yahoo Finance",
                "suggestion": "Try again in a few minutes",
                "estimated_scores": {
                    "environmental_score": 55.0,
                    "social_score": 58.0,
                    "governance_score": 62.0,
                    "total_esg_score": 58.0
                },
                "data_quality": "unavailable"
            }
        else:
            esg_data_result = {
                "error": f"HTTP Error {e.response.status_code}: {str(e)}",
                "data_quality": "error"
            }
    
    except Exception as e:
        esg_data_result = {
            "error": f"Could not fetch ESG data: {str(e)}",
            "data_quality": "error"
        }
    
    # Fetch financial data
    financial_data_result = None
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        financial = db.query(models.FinancialMetric).filter(
            models.FinancialMetric.company_id == company.id,
            models.FinancialMetric.date == date.today()
        ).first()
        
        if financial:
            financial.pe_ratio = convert_numpy_to_python(info.get('trailingPE'))
            financial.eps = convert_numpy_to_python(info.get('trailingEps'))
            financial.revenue = convert_numpy_to_python(info.get('totalRevenue'))
            financial.profit_margin = convert_numpy_to_python(info.get('profitMargins'))
            financial.debt_to_equity = convert_numpy_to_python(info.get('debtToEquity'))
        else:
            financial = models.FinancialMetric(
                company_id=company.id,
                pe_ratio=convert_numpy_to_python(info.get('trailingPE')),
                eps=convert_numpy_to_python(info.get('trailingEps')),
                revenue=convert_numpy_to_python(info.get('totalRevenue')),
                profit_margin=convert_numpy_to_python(info.get('profitMargins')),
                debt_to_equity=convert_numpy_to_python(info.get('debtToEquity')),
                date=date.today()
            )
            db.add(financial)
        
        db.commit()
        
        financial_data_result = {
            "pe_ratio": financial.pe_ratio,
            "eps": financial.eps,
            "revenue": financial.revenue,
            "profit_margin": financial.profit_margin,
            "debt_to_equity": financial.debt_to_equity,
            "data_quality": "actual"
        }
    
    except Exception as e:
        financial_data_result = {
            "error": f"Could not fetch financial data: {str(e)}",
            "data_quality": "error"
        }
    
    return {
        "symbol": symbol,
        "name": company.name,
        "sector": company.sector,
        "industry": company.industry,
        "data_source": "Yahoo Finance API",
        "fetch_time": datetime.now().isoformat(),
        "esg_data": esg_data_result,
        "financial_data": financial_data_result
    }

@app.put("/companies/{symbol}", tags=["Companies"])
def update_company(
    symbol: str,
    company_update: schemas.CompanyUpdate,
    db: Session = Depends(get_db)
):
    """
    Update company information
    
    **Example:** 
    ```json
    {
        "name": "Apple Inc. (Updated)",
        "sector": "Technology",
        "industry": "Consumer Electronics"
    }
    ```
    """
    db_company = db.query(models.Company).filter(
        models.Company.symbol == symbol.upper()
    ).first()
    
    if not db_company:
        raise HTTPException(status_code=404, detail=f"Company {symbol} not found")
    
    for key, value in company_update.dict(exclude_unset=True).items():
        setattr(db_company, key, value)
    
    db.commit()
    db.refresh(db_company)
    
    return {
        "message": f"Company {symbol} updated successfully",
        "company": {
            "id": db_company.id,
            "symbol": db_company.symbol,
            "name": db_company.name,
            "sector": db_company.sector,
            "industry": db_company.industry,
            "market_cap": db_company.market_cap
        }
    }

@app.delete("/companies/{symbol}", tags=["Companies"])
def delete_company(symbol: str, db: Session = Depends(get_db)):
    """
    Delete a specific company
    
    **Example:** `DELETE /companies/AAPL`
    """
    db_company = db.query(models.Company).filter(
        models.Company.symbol == symbol.upper()
    ).first()
    
    if not db_company:
        raise HTTPException(status_code=404, detail=f"Company {symbol} not found")
    
    db.delete(db_company)
    db.commit()
    
    return {
        "message": f"Company {symbol} deleted successfully",
        "deleted_symbol": symbol.upper()
    }

@app.delete("/companies/", tags=["Companies"])
def delete_all_companies(
    confirm: bool = Query(False, description="Set to true to confirm deletion"),
    db: Session = Depends(get_db)
):
    """
    ⚠️ **DELETE ALL COMPANIES** (Use with extreme caution!)
    
    **Requires confirmation parameter:** `?confirm=true`
    
    This will delete **ALL companies** and **ALL related data**:
    - ESG scores
    - Financial metrics
    - Stock prices
    
    **This action CANNOT be undone!**
    
    **Example:** `DELETE /companies/?confirm=true`
    """
    
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Confirmation required",
                "message": "To delete all companies, add ?confirm=true to the URL",
                "warning": "⚠️ This action cannot be undone!",
                "example": "DELETE /companies/?confirm=true"
            }
        )
    
    try:
        # Count before deletion
        count = db.query(models.Company).count()
        
        if count == 0:
            return {
                "message": "No companies to delete",
                "deleted_count": 0
            }
        
        # Delete all companies (cascade will delete related data)
        db.query(models.Company).delete()
        db.commit()
        
        return {
            "message": "✅ All companies deleted successfully",
            "deleted_count": count,
            "warning": "All related ESG scores, financial data, and stock prices were also deleted",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting companies: {str(e)}"
        )

# ============================================================================
# ANALYTICS & KPI ENDPOINTS
# ============================================================================

@app.get("/analytics/portfolio/average-esg", tags=["Analytics"])
def get_portfolio_average_esg(
    symbols: str = Query(
        ...,
        description="Comma-separated symbols: AAPL,MSFT or AAPL, MSFT or {AAPL, MSFT}",
        example="AAPL,MSFT,GOOGL"
    ),
    db: Session = Depends(get_db)
):
    """
    Calculate portfolio-weighted average ESG score
    
    **Supports multiple input formats:**
    - `AAPL,MSFT,GOOGL`
    - `AAPL, MSFT, GOOGL` (with spaces)
    - `{AAPL, MSFT, GOOGL}` (with braces)
    - `AAPL , MSFT , GOOGL` (flexible spacing)
    
    **Example:** `/analytics/portfolio/average-esg?symbols=AAPL,MSFT,GOOGL`
    """
    
    # Clean input - handle all formats
    symbols_clean = symbols.strip().replace('{', '').replace('}', '')
    symbol_list = [s.strip().upper() for s in symbols_clean.split(',') if s.strip()]
    
    if not symbol_list:
        raise HTTPException(
            status_code=400,
            detail="No valid symbols provided. Use format: AAPL,MSFT,GOOGL"
        )
    
    # Get ESG data with market cap
    results = db.query(
        models.Company.symbol,
        models.Company.name,
        models.Company.market_cap,
        models.ESGScore.total_esg_score,
        models.ESGScore.environmental_score,
        models.ESGScore.social_score,
        models.ESGScore.governance_score
    ).join(models.ESGScore).filter(
        models.Company.symbol.in_(symbol_list)
    ).all()
    
    if not results:
        # Show available companies
        all_companies = db.query(models.Company.symbol).limit(20).all()
        available = [c[0] for c in all_companies]
        
        raise HTTPException(
            status_code=404,
            detail={
                "error": "No ESG data found for provided symbols",
                "requested_symbols": symbol_list,
                "sample_available_symbols": available,
                "total_companies_in_db": db.query(models.Company).count(),
                "suggestion": "Run 'python -m scripts.data_import' to import data, or use GET /companies/{symbol}/fetch-live-data"
            }
        )
    
    found_symbols = [r.symbol for r in results]
    missing_symbols = [s for s in symbol_list if s not in found_symbols]
    
    # Calculate weighted average
    total_market_cap = sum(r.market_cap for r in results if r.market_cap)
    
    if total_market_cap == 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid market cap data for companies"
        )
    
    weighted_score = sum(
        (r.total_esg_score or 0) * (r.market_cap / total_market_cap)
        for r in results if r.total_esg_score and r.market_cap
    )
    
    response = {
        "portfolio_symbols": symbol_list,
        "found_companies": len(results),
        "average_esg_score": round(weighted_score, 2),
        "total_market_cap": total_market_cap,
        "calculation_method": "Market-cap weighted average",
        "companies": [
            {
                "symbol": r.symbol,
                "name": r.name,
                "esg_score": r.total_esg_score,
                "environmental_score": r.environmental_score,
                "social_score": r.social_score,
                "governance_score": r.governance_score,
                "market_cap": r.market_cap,
                "weight_percent": round((r.market_cap / total_market_cap) * 100, 2)
            }
            for r in results
        ]
    }
    
    # Add warning if some symbols were not found
    if missing_symbols:
        response["warning"] = f"Data not found for: {', '.join(missing_symbols)}"
        response["missing_symbols"] = missing_symbols
    
    return response

@app.get("/analytics/top-performers", tags=["Analytics"])
def get_top_esg_performers(
    limit: int = Query(10, ge=1, le=100, description="Number of companies to return"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    metric: str = Query("total", description="Sort by: total, environmental, social, governance"),
    db: Session = Depends(get_db)
):
    """
    Get top ESG performing companies
    
    **Sorting options:**
    - `total` - Total ESG score (default)
    - `environmental` - Environmental score
    - `social` - Social score
    - `governance` - Governance score
    
    **Example:** `/analytics/top-performers?limit=10&sector=Technology&metric=environmental`
    """
    
    # Determine sort column
    sort_column_map = {
        "total": models.ESGScore.total_esg_score,
        "environmental": models.ESGScore.environmental_score,
        "social": models.ESGScore.social_score,
        "governance": models.ESGScore.governance_score
    }
    
    sort_column = sort_column_map.get(metric, models.ESGScore.total_esg_score)
    
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
    
    results = query.order_by(desc(sort_column)).limit(limit).all()
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "No companies found with ESG data",
                "filters": {"sector": sector, "limit": limit, "metric": metric},
                "suggestion": "Try removing sector filter or run data import"
            }
        )
    
    return {
        "filter": {
            "sector": sector,
            "limit": limit,
            "sort_by": metric
        },
        "found": len(results),
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
    """
    Get average ESG scores by sector
    
    Shows distribution and average scores across all sectors
    
    **Example:** `/analytics/sector-distribution`
    """
    results = db.query(
        models.Company.sector,
        func.avg(models.ESGScore.total_esg_score).label('avg_esg'),
        func.avg(models.ESGScore.environmental_score).label('avg_environmental'),
        func.avg(models.ESGScore.social_score).label('avg_social'),
        func.avg(models.ESGScore.governance_score).label('avg_governance'),
        func.count(models.Company.id).label('company_count')
    ).join(models.ESGScore).group_by(models.Company.sector).all()
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "No ESG data available",
                "suggestion": "Run 'python -m scripts.data_import' to import data"
            }
        )
    
    sectors_data = [
        {
            "sector": r.sector,
            "average_esg_score": round(r.avg_esg, 2) if r.avg_esg else None,
            "average_environmental": round(r.avg_environmental, 2) if r.avg_environmental else None,
            "average_social": round(r.avg_social, 2) if r.avg_social else None,
            "average_governance": round(r.avg_governance, 2) if r.avg_governance else None,
            "num_companies": r.company_count
        }
        for r in results
    ]
    
    # Calculate overall statistics
    total_companies = sum(s['num_companies'] for s in sectors_data)
    overall_avg = sum(s['average_esg_score'] * s['num_companies'] for s in sectors_data if s['average_esg_score']) / total_companies if total_companies > 0 else 0
    
    return {
        "total_sectors": len(results),
        "total_companies": total_companies,
        "overall_average_esg": round(overall_avg, 2),
        "sectors": sectors_data
    }

@app.get("/analytics/risk-flags", tags=["Analytics"])
def get_risk_flags(
    controversy_threshold: float = Query(5.0, ge=0, le=10, description="Controversy score threshold"),
    db: Session = Depends(get_db)
):
    """
    Identify companies with ESG risk flags
    
    **Controversy Score Scale:**
    - 0-3: Low risk
    - 4-6: Medium risk
    - 7-10: High risk
    
    **Example:** `/analytics/risk-flags?controversy_threshold=5.0`
    """
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
        "total_flagged": len(results),
        "risk_levels": {
            "high": len([r for r in results if r.controversy_score >= 7]),
            "medium": len([r for r in results if 4 <= r.controversy_score < 7]),
            "low": len([r for r in results if r.controversy_score < 4])
        },
        "high_risk_companies": [
            {
                "symbol": r.symbol,
                "name": r.name,
                "sector": r.sector,
                "controversy_score": r.controversy_score,
                "esg_score": r.total_esg_score,
                "risk_level": "High" if r.controversy_score >= 7 else ("Medium" if r.controversy_score >= 4 else "Low")
            }
            for r in results
        ]
    }

# ============================================================================
# SECTORS ENDPOINT
# ============================================================================

@app.get("/sectors/", tags=["Sectors"])
def get_sectors(db: Session = Depends(get_db)):
    """
    Get list of all available sectors
    
    **Example:** `/sectors/`
    """
    sectors = db.query(models.Company.sector).distinct().all()
    sector_list = [s[0] for s in sectors if s[0]]
    
    # Get company count per sector
    sector_counts = db.query(
        models.Company.sector,
        func.count(models.Company.id).label('count')
    ).group_by(models.Company.sector).all()
    
    return {
        "total_sectors": len(sector_list),
        "sectors": [
            {
                "name": sc.sector,
                "company_count": sc.count
            }
            for sc in sector_counts if sc.sector
        ]
    }
