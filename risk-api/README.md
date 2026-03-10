# 📊 Stock Valuation & Risk Analytics API

> A comprehensive RESTful API for stock market analysis, valuation metrics, and risk assessment

[FastAPI](https://fastapi.tiangolo.com)
[Python](https://www.python.org)
[PostgreSQL](https://www.postgresql.org)

---

## 🎯 Project Overview

This API provides financial analysis tools for stock market investors:

- **Stock Valuation**: Identify undervalued/overvalued stocks using P/E ratios
- **Risk Assessment**: Calculate volatility and risk classifications  
- **Portfolio Analytics**: Track multi-stock portfolio performance
- **Sector Comparison**: Compare financial metrics across industries
- **Real-time Data**: Integration with Yahoo Finance API

**Project Evolution**: Originally planned as an ESG Investment API, the project pivoted to financial valuation after encountering persistent API rate limiting issues with ESG data sources. See Technical Report for detailed explanation of this strategic decision.

---

## 🏗️ Technology Stack


| Component           | Technology   | Version      | Purpose                                     |
| ------------------- | ------------ | ------------ | ------------------------------------------- |
| **Web Framework**   | FastAPI      | 0.109.0      | High-performance async API framework        |
| **Database**        | PostgreSQL   | 16+          | Relational data storage with CASCADE DELETE |
| **ORM**             | SQLAlchemy   | 2.0.25       | Database abstraction layer                  |
| **Data Source**     | yfinance     | 0.2.36       | Yahoo Finance API wrapper                   |
| **Data Processing** | Pandas/NumPy | 2.2.0/1.26.3 | Financial calculations                      |
| **Server**          | Uvicorn      | 0.27.0       | ASGI production server                      |
| **Testing**         | pytest       | 8.0.0        | Automated testing framework                 |


---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **PostgreSQL 16+** ([Download](https://www.postgresql.org/download/))
- **Git** ([Download](https://git-scm.com/downloads))

### Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/errorstd/stock-valuation-api.git
---


```bash
git clone https://github.com/errorstd/COMP3011.git
cd COMP3011/risk-api
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4.🗄️ Database Setup

Create .env file in project root:

```text
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/stock_api
```

### 5. Initialize Database

```bash
python .\scripts\init_db.py
```

Expected output:

```text
🗄️  Creating all database tables...
✅ Database tables created successfully!
```

### 6. Import Stock Data

```bash
python -m scripts.data_import
```

### 7. Start API Server

```bash
uvicorn app.main:app --reload


Output:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### 8. Access Documentation

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🧪 Testing

### Run All Tests

```bash
python .\tests\run_all_tests.py
```

This executes:

- Database tests (connection, CASCADE DELETE, foreign keys)
- API tests (endpoints, response formats)
- Analytics tests (calculation accuracy)

### Run Individual Test Suites

```bash
# Database tests
python tests/test_db_connection.py

# API endpoint tests
python tests/test_api.py

# Analytics logic tests
python tests/test_analytics.py
```

Manual Testing via Swagger UI

1. Open: [http://localhost:8000/docs](http://localhost:8000/docs)
2. Click "Try it out" on any endpoint
3. Fill parameters and click "Execute"
4. View response

## 📚 API Documentation

### Core Endpoints (27 Total)

### 🏢 Companies Management

| Method | Endpoint                 | Description                                |
| ------ | ------------------------ | ------------------------------------------ |
| GET    | /companies/              | List all companies or get specific company |
| POST   | /companies/single        | Create a single company from JSON          |
| POST   | /companies/bulk          | Bulk upload companies from CSV file        |
| DELETE | /companies/{symbol}      | Delete specific company (CASCADE)          |
| DELETE | /companies/?confirm=true | Delete all companies (CASCADE)             |

### 🔄 Real-Time Updates **(NEW)**

| Method | Endpoint                      | Description                                      |
| ------ | ----------------------------- | ------------------------------------------------ |
| PUT    | /companies/{symbol}/update    | Update single stock with real-time data          |
| PUT    | /companies/update-all         | Bulk update multiple stocks (up to 50)           |
| GET    | /companies/{symbol}/live      | Get live quote directly from Yahoo Finance       |

### 💰 Valuation Analytics

| Method | Endpoint                         | Description                       |
| ------ | -------------------------------- | --------------------------------- |
| GET    | /analytics/valuation/undervalued | Find undervalued stocks (low P/E) |
| GET    | /analytics/valuation/overvalued  | Find overvalued stocks (high P/E) |

### ⚠️ Risk Assessment

| Method | Endpoint                            | Description                |
| ------ | ----------------------------------- | -------------------------- |
| GET    | /analytics/risk/volatility/{symbol} | Calculate stock volatility |
| GET    | /analytics/risk/high-risk           | Identify high-risk stocks  |

### 📊 Portfolio & Sectors

| Method | Endpoint                         | Description               |
| ------ | -------------------------------- | ------------------------- |
| GET    | /analytics/portfolio/performance | Analyze portfolio metrics |
| GET    | /analytics/sectors/comparison    | Compare sectors           |
| GET    | /sectors/                        | List all sectors          |

### 🔍 Browse & Search

| Method | Endpoint               | Description                     |
| ------ | ---------------------- | ------------------------------- |
| GET    | /browse/search?query=X | Search stocks by name or symbol |
| GET    | /browse/categories     | Get all sectors and industries  |
| GET    | /browse/new-stocks     | Recently added stocks           |
| GET    | /browse/tech-stocks    | Technology sector stocks        |
| GET    | /browse/green-energy   | Green/renewable energy stocks   |




Example Usage
Find Undervalued Stocks:

```bash
curl "http://localhost:8000/analytics/valuation/undervalued?limit=10&max_pe=15"
```

Calculate Stock Volatility:

```bash
curl "http://localhost:8000/analytics/risk/volatility/AAPL"
```

Search Stocks:

```bash
curl "http://localhost:8000/browse/search?query=apple"
```

Portfolio Performance:

```bash
curl "http://localhost:8000/analytics/portfolio/performance?symbols=AAPL,MSFT,GOOGL"
```

## 🗄️ Database Schema

```text
companies (parent)
├── financial_metrics (CASCADE DELETE)
├── stock_prices (CASCADE DELETE)
└── esg_scores (CASCADE DELETE)
```

Key Features:

- CASCADE DELETE: Deleting company automatically removes all related data
- Indexed columns: symbol, company_id, date for fast queries
- Foreign key constraints: Ensures referential integrity

## 📁 Project Structure

```text
stock-valuation-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI endpoints
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   └── database.py          # Database config
│   ├── routers/             # (Optional) Route modules
│   └── exceptions.py        # Custom error handlers
├── scripts/
│   ├── __init__.py
│   ├── data_import.py       # Data import (150 companies)
│   └── init_db.py           # Database initialization
├── tests/
│   ├── __init__.py
│   ├── run_all_tests.py        # Test runner
│   ├── test_db_connection.py    # Database tests
│   ├── test_api.py              # API endpoint tests
│   └── test_analytics.py        # Analytics logic tests
├── notebooks/
│   └── data_exploration.ipynb
├── data/
│   └── .gitkeep
├── .env                     # Environment variables
├── .gitignore
├── requirements.txt         # Dependencies
├── README.md               # This file
└── Technical_Report.pdf    # Academic documentation
```

## 🎓 Academic Context

### Module: COMP3011 - Web Services and Web Data

### University: University of Leeds

### Academic Year: 2025/2026

### Key Learning Outcomes Demonstrated:

- RESTful API design and implementation
- Database design with relational integrity
- External API integration

-Financial domain modeling

- Automated testing practices
- Technical documentation

### 📝 License

- API Key: None required! ✅
- Rate Limit: None for basic data

### Data Coverage:S

- 50 companies across 5 sectors
- 5 sectors: Technology, Finance, Healthcare, Energy, Consumer
- 30 days of historical stock prices
- Real-time ESG scores from Yahoo Finance/Sustainalytics

