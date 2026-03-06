"""
Stock Valuation & Risk Analytics Data Import
Focuses on RELIABLE Yahoo Finance data (no ESG dependency)
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

# 50 companies across sectors (ESG removed - financial data only)
COMPANIES = {
    'Technology': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'TSLA', 'AMD', 'INTC', 'CRM', 'ORCL'],
    'Finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB'],
    'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT', 'MRK', 'LLY', 'BMY', 'AMGN'],
    'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL'],
    'Consumer': ['AMZN', 'WMT', 'HD', 'PG', 'KO', 'PEP', 'COST', 'NKE', 'MCD', 'SBUX']
}

def convert_numpy(value):
    """Convert numpy types to Python native types"""
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (np.integer, np.floating)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.item()
    return value

def import_company_data(symbol: str, sector: str, db: Session):
    """Import company basic information"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        existing = db.query(Company).filter(Company.symbol == symbol).first()
        if existing:
            print(f"  ⏭️  {symbol} already exists, skipping...")
            return existing
        
        company = Company(
            symbol=symbol,
            name=info.get('longName', symbol),
            sector=sector,
            industry=info.get('industry', 'Unknown'),
            market_cap=convert_numpy(info.get('marketCap', 0))
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
        
        existing = db.query(FinancialMetric).filter(
            FinancialMetric.company_id == company_id,
            FinancialMetric.date == date.today()
        ).first()
        
        if existing:
            print(f"    ⏭️  Financial data for {symbol} already exists")
            return
        
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
        hist = ticker.history(period="3mo")  # 90 days for better analytics
        
        if hist.empty:
            print(f"    ⚠️  No price data for {symbol}")
            return
        
        imported_count = 0
        for index, row in hist.iterrows():
            price_date = index.date()
            
            existing = db.query(StockPrice).filter(
                StockPrice.company_id == company_id,
                StockPrice.date == price_date
            ).first()
            
            if existing:
                continue
            
            stock_price = StockPrice(
                company_id=company_id,
                date=price_date,
                open=float(row['Open']),
                close=float(row['Close']),
                volume=int(row['Volume'])
            )
            
            db.add(stock_price)
            imported_count += 1
        
        db.commit()
        print(f"    ✅ Stock prices imported for {symbol} ({imported_count} days)")
        
    except Exception as e:
        print(f"    ❌ Error importing prices for {symbol}: {e}")
        db.rollback()

def run_full_import():
    """Run complete data import"""
    
    print("\n" + "="*70)
    print("🚀 Stock Valuation & Risk Analytics - Data Import")
    print("="*70 + "\n")
    
    total_companies = sum(len(symbols) for symbols in COMPANIES.values())
    current = 0
    successful = 0
    failed = 0
    
    for sector, symbols in COMPANIES.items():
        print(f"\n📊 Importing {sector} sector...")
        
        for symbol in symbols:
            current += 1
            print(f"\n[{current}/{total_companies}] Processing {symbol}...")
            
            db = SessionLocal()
            
            try:
                company = import_company_data(symbol, sector, db)
                
                if company:
                    import_financial_data(symbol, company.id, db)
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
            
            time.sleep(1.5)  # Rate limiting
    
    print("\n" + "="*70)
    print("✅ Data import completed!")
    print("="*70)
    print(f"\n📈 Summary:")
    print(f"   Total companies: {total_companies}")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"\n🎯 Focus: Stock Valuation & Risk Analytics (Financial Data Only)")

if __name__ == "__main__":
    run_full_import()
