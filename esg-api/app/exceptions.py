# Custom exceptions for the API

# app/exceptions.py
from fastapi import HTTPException, status

class CompanyNotFoundError(HTTPException):
    def __init__(self, symbol: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with symbol '{symbol}' not found"
        )

class InvalidESGScoreError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ESG scores must be between 0 and 100"
        )

# In main.py - Add error handler
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )
