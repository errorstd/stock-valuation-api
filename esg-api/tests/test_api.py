"""
Test API endpoints
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_company():
    response = client.post(
        "/companies/",
        json={
            "symbol": "TEST",
            "name": "Test Company",
            "sector": "Technology",
            "market_cap": 1000000000
        }
    )
    assert response.status_code == 200
    assert response.json()["symbol"] == "TEST"

def test_read_companies():
    response = client.get("/companies/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_portfolio_average_esg():
    response = client.get("/analytics/portfolio/average-esg?symbols=AAPL,MSFT")
    assert response.status_code == 200
    assert "average_esg_score" in response.json()

# Run tests: pytest tests/
