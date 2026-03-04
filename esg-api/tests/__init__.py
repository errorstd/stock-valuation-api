"""
Test API endpoints
"""

import yfinance as yf

# Download data for Apple
aapl = yf.Ticker("AAPL")
print(aapl.info)  # Company info
print(aapl.history(period="1mo"))  # Price data
