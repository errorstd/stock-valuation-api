# app/api/v1/endpoints/kpis.py
@router.get("/kpis/portfolio/{id}/esg-summary")
async def portfolio_esg_summary(id: int, db: Session = Depends(get_db)):
    # Complex aggregation only possible because data is in YOUR DB
    holdings = db.query(Holding).filter(Holding.portfolio_id == id).all()
    
    # Calculate weighted average ESG score
    total_value = sum(h.shares * h.company.price for h in holdings)
    weighted_esg = sum(
        (h.shares * h.company.price / total_value) * h.company.latest_esg_score.total_score
        for h in holdings
    )
    
    return {
        "portfolio_id": id,
        "avg_esg_score": weighted_esg,
        "holdings_count": len(holdings),
        "sector_breakdown": {...}  # More complex logic
    }
