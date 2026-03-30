# =========================================================
# Stock Routes
# =========================================================
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.services.data_loader import load_all_stocks
from app.services.stock_service import (
    get_stock_data,
    follow_stock,
    unfollow_stock,
    get_user_stocks,
    get_top_movers,
    get_risk_analysis,
    get_performance,
    get_prediction
)
from app.models.company import Company
from app.models.user import User
from app.utils.response import success_response

# =========================================================
# Router Configuration
# =========================================================
router = APIRouter(prefix="/stocks", tags=["Stocks"])

# =========================================================
# Load Data
# =========================================================
@router.post("/load-all/", status_code=status.HTTP_200_OK)
def load_all(db: Session = Depends(get_db)):
    results = load_all_stocks(db)
    return success_response(
        message="All stock data loaded",
        data=results
    )

# =========================================================
# Get Stock Data
# =========================================================
@router.get("/data/{symbol}")
def get_data(symbol: str, db: Session = Depends(get_db)):
    stocks = get_stock_data(db, symbol)

    if not stocks:
        raise HTTPException(404, "No data found")

    return success_response(
        message="Stock data fetched successfully",
        data=stocks
    )

# =========================================================
# Get Companies
# =========================================================
@router.get("/companies")
def get_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).all()

    result = [
        {
            "symbol": c.symbol,
            "name": c.name,
            "sector": c.sector
        }
        for c in companies
    ]

    return success_response(
        message="Companies fetched successfully",
        data=result
    )


# =========================================================
# Summary
# =========================================================
@router.get("/summary/{symbol}")
def get_summary(symbol: str, db: Session = Depends(get_db)):
    stocks = get_stock_data(db, symbol, limit=365)

    if not stocks:
        raise HTTPException(404, "No data")

    result = {
        "symbol": symbol,
        "52_week_high": max(s["high"] for s in stocks),
        "52_week_low": min(s["low"] for s in stocks),
        "average_close": round(
            sum(s["close"] for s in stocks) / len(stocks), 2
        )
    }

    return success_response(
        message="Summary fetched successfully",
        data=result
    )


# =========================================================
# Compare
# =========================================================
@router.get("/compare")
def compare(symbol1: str, symbol2: str, db: Session = Depends(get_db)):
    s1 = get_stock_data(db, symbol1, limit=1)
    s2 = get_stock_data(db, symbol2, limit=1)

    if not s1 or not s2:
        raise HTTPException(404, "Data missing")

    result = {
        "symbol1": symbol1,
        "symbol2": symbol2,
        "latest_close_1": s1[0]["close"],
        "latest_close_2": s2[0]["close"]
    }

    return success_response(
        message="Comparison fetched successfully",
        data=result
    )


# =========================================================
# Follow Stock
# =========================================================
@router.post("/follow/{symbol}")
def follow(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = follow_stock(db, current_user.id, symbol)

    return success_response(
        message=result["message"]
    )


# =========================================================
# Unfollow Stock
# =========================================================
@router.delete("/unfollow/{symbol}")
def unfollow(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = unfollow_stock(db, current_user.id, symbol)

    return success_response(
        message=result["message"]
    )

# =========================================================
# User Stocks 
# =========================================================
@router.get("/my-stocks")
def my_stocks(
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = get_user_stocks(db, current_user.id, skip, limit)

    return success_response(
        message="User stocks fetched successfully",
        data=result
    )

# =========================================================
# Top Movers
# =========================================================
@router.get("/top-movers")
def top_movers(db: Session = Depends(get_db)):
    result = get_top_movers(db)

    return success_response(
        message="Top movers fetched successfully",
        data=result
    )


# =========================================================
# Risk Analysis
# =========================================================
@router.get("/risk/{symbol}")
def risk(symbol: str, db: Session = Depends(get_db)):
    result = get_risk_analysis(db, symbol)

    return success_response(
        message="Risk analysis fetched successfully",
        data=result
    )

# =========================================================
# Performance
# =========================================================
@router.get("/performance/{symbol}")
def performance(symbol: str, days: int = 30, db: Session = Depends(get_db)):
    result = get_performance(db, symbol, days)

    return success_response(
        message="Performance fetched successfully",
        data=result
    )

# =========================================================
# Prediction
# =========================================================
@router.get("/predict/{symbol}")
def predict(symbol: str, db: Session = Depends(get_db)):
    result = get_prediction(db, symbol)

    return success_response(
        message="Prediction fetched successfully",
        data=result
    )
    