# app/api/v1/endpoints/companies.py
@router.get("/companies/{ticker}")
async def get_company(ticker: str, db: Session = Depends(get_db)):
    # Query YOUR database, not external API
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

