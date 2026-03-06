"""
Database Initialization Script
Creates all tables defined in models.py
"""

import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine, Base
from app.models import Company, ESGScore, FinancialMetric, StockPrice

def init_database():
    """Create all database tables"""
    try:
        # Create engine
        print("🗄️  Creating all database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        print("\nCreated tables:")
        print("  - companies")
        print("  - esg_scores")
        print("  - financial_metrics")
        print("  - stock_prices")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your DATABASE_URL in .env file")
        print("3. Verify database 'esg_investment_db' exists")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
