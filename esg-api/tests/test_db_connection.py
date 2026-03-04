"""
Test PostgreSQL connection
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:YourPassword@localhost:5432/esg_investment_db")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()
        print("✅ Database connection successful!")
        print(f"PostgreSQL version: {version[0]}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting steps:")
    print("1. Check if PostgreSQL service is running (Services.msc → postgresql-x64-15)")
    print("2. Verify password in .env file")
    print("3. Ensure database 'esg_investment_db' exists")
