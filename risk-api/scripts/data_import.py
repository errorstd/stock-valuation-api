"""
Stock Valuation & Risk Analytics - Data Import
EXPANDED: 160 companies across multiple categories
"""

import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yfinance as yf
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from app.database import SessionLocal
from app.models import Company, FinancialMetric, StockPrice
import time


# ============================================================================
# 160 COMPANIES ACROSS 8 CATEGORIES
# ============================================================================

COMPANIES = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "TSLA", "AMD", "INTC", 
                   "CRM", "ORCL", "ADBE", "CSCO", "AVGO", "QCOM", "TXN", "AMAT", 
                   "MU", "LRCX", "KLAC", "SNPS"],
    
    "Finance": ["JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "BLK", "SCHW", "USB",
                "PNC", "TFC", "COF", "BK", "STT", "FITB", "HBAN", "RF", "CFG", "KEY"],
    
    "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "TMO", "ABT", "MRK", "LLY", "BMY", 
                   "AMGN", "GILD", "CVS", "CI", "REGN", "ISRG", "VRTX", "ZTS", 
                   "BIIB", "ILMN", "MRNA"],
    
    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
               "KMI", "WMB", "HES", "DVN", "FANG", "MRO", "APA", "CTRA", "BKR", "NOV"],
    
    "Consumer": ["AMZN", "WMT", "HD", "PG", "KO", "PEP", "COST", "NKE", "MCD", "SBUX",
                 "TGT", "LOW", "DG", "DLTR", "ROST", "TJX", "BBY", "ULTA", "LULU", "EBAY"],
    
    "Green Energy": ["NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "XEL", "ED", "ES",
                     "ENPH", "SEDG", "FSLR", "RUN", "PLUG", "BE", "NOVA", "VWDRY", "CSIQ", "JKS"],
    
    "Data & AI": ["SNOW", "PLTR", "NET", "DDOG", "MDB", "CRWD", "ZS", "OKTA", "TEAM", 
                  "WDAY", "SPLK", "FTNT", "PANW", "CYBR", "TENB", "VRNS", "S", "ZI", 
                  "ESTC", "CFLT"],
    
    "New Tech": ["UBER", "LYFT", "ABNB", "DASH", "COIN", "RBLX", "U", "PATH", "HOOD", 
                 "SOFI", "AFRM", "SQ", "PYPL", "SHOP", "ROKU", "PINS", "SNAP", "TWLO", 
                 "ZM", "DOCU"]
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def convert_numpy(value):
    """Convert numpy types to Python native types"""
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (np.integer, np.floating)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.item()
    return value


# ============================================================================
# IMPORT FUNCTIONS
# ============================================================================

def import_company_data(symbol: str, sector: str, db: Session):
    """Import company basic information"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Check if already exists
        existing = db.query(Company).filter(Company.symbol == symbol).first()
        if existing:
            print(f"  ✓ {symbol} already exists, skipping...")
            return existing
        
        # Create company
        company = Company(
            symbol=symbol,
            name=info.get('longName', symbol),
            sector=sector,
            industry=info.get('industry', 'Unknown'),
            marketcap=convert_numpy(info.get('marketCap', 0))  # ✅ FIXED: no underscore
        )
        
        db.add(company)
        db.commit()
        db.refresh(company)
        
        print(f"  ✅ Imported {symbol} - {company.name}")
        return company
        
    except Exception as e:
        print(f"  ❌ Error importing {symbol}: {e}")
        db.rollback()
        return None


def import_financial_data(symbol: str, company_id: int, db: Session):
    """Import comprehensive financial metrics"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Check if already exists
        existing = db.query(FinancialMetric).filter(
            FinancialMetric.company_id == company_id,
            FinancialMetric.date == date.today()
        ).first()
        
        if existing:
            print(f"    ✓ Financial data for {symbol} already exists")
            return
        
        # Create financial metric
        financial = FinancialMetric(
            company_id=company_id,
            pe_ratio=convert_numpy(info.get('trailingPE')),
            eps=convert_numpy(info.get('trailingEps')),
            revenue=convert_numpy(info.get('totalRevenue')),
            profit_margin=convert_numpy(info.get('profitMargins')),
            debt_to_equity=convert_numpy(info.get('debtToEquity')),
            date=date.today()
        )
        
        db.add(financial)
        db.commit()
        print(f"    ✅ Financial metrics imported for {symbol}")
        
    except Exception as e:
        print(f"    ❌ Error importing financials for {symbol}: {e}")
        db.rollback()


def import_stock_prices(symbol: str, company_id: int, db: Session):
    """Import 90 days of historical price data"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='3mo')
        
        if hist.empty:
            print(f"    ⚠️  No price data for {symbol}")
            return
        
        imported_count = 0
        
        for index, row in hist.iterrows():
            price_date = index.date()
            
            # Check if already exists
            existing = db.query(StockPrice).filter(
                StockPrice.company_id == company_id,
                StockPrice.date == price_date
            ).first()
            
            if existing:
                continue
            
            # Create stock price
            stock_price = StockPrice(
                company_id=company_id,
                date=price_date,
                open=float(row['Open']),
                close=float(row['Close']),
                high=float(row['High']) if 'High' in row else None,
                low=float(row['Low']) if 'Low' in row else None,
                volume=int(row['Volume'])
            )
            
            db.add(stock_price)
            imported_count += 1
        
        db.commit()
        print(f"    ✅ Stock prices imported for {symbol}: {imported_count} days")
        
    except Exception as e:
        print(f"    ❌ Error importing prices for {symbol}: {e}")
        db.rollback()


# ============================================================================
# MAIN IMPORT
# ============================================================================

def run_full_import():
    """Run complete data import"""
    print("=" * 70)
    print("🚀 Stock Valuation & Risk Analytics - EXPANDED Data Import")
    print("=" * 70)
    
    total_companies = sum(len(symbols) for symbols in COMPANIES.values())
    current = 0
    successful = 0
    failed = 0
    
    for sector, symbols in COMPANIES.items():
        print(f"\n📊 Importing {sector} sector... ({len(symbols)} companies)\n")
        
        for symbol in symbols:
            current += 1
            print(f"[{current}/{total_companies}] Processing {symbol}...")
            
            db = SessionLocal()
            try:
                # Import company
                company = import_company_data(symbol, sector, db)
                
                if company:
                    # Import financial data
                    import_financial_data(symbol, company.id, db)
                    
                    # Import stock prices
                    import_stock_prices(symbol, company.id, db)
                    
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                print(f"  ❌ Unexpected error for {symbol}: {e}")
                failed += 1
                db.rollback()
            finally:
                db.close()
            
            # Rate limiting to avoid overwhelming Yahoo Finance
            time.sleep(1.5)
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ Data import completed!")
    print("=" * 70)
    print(f"Summary:")
    print(f"  Total companies: {total_companies}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Success rate: {(successful/total_companies)*100:.1f}%")
    print(f"  Categories: {', '.join(COMPANIES.keys())}")


if __name__ == "__main__":
    run_full_import()
