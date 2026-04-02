# =========================================================
# Stock Routes
# =========================================================
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.core import get_db, get_current_user
from app.services import (
    load_all_stocks,
    get_stock_data,
    follow_stock,
    unfollow_stock,
    get_user_stocks,
    get_top_movers,
    get_risk_analysis,
    get_performance,
    get_prediction
)
from app.models import Company, User
from app.schemas import (
    SuccessResponse
)
from app.utils.response import success_response

# =========================================================
# Router Configuration
# =========================================================
router = APIRouter(prefix="/stocks", tags=["Stocks"])

# =========================================================
# Load Data
# =========================================================
@router.post(
    "/load-all/",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse
)
def load_all(db: Session = Depends(get_db)):
    results = load_all_stocks(db)

    return success_response(
        message="All stock data loaded",
        data=results
    )


# =========================================================
# Get Stock Data
# =========================================================
@router.get(
    "/data/{symbol}",
    response_model=SuccessResponse
)
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
@router.get("/companies", response_model=SuccessResponse)
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
@router.get(
    "/summary/{symbol}",
    response_model=SuccessResponse
)
def get_summary(symbol: str, db: Session = Depends(get_db)):
    stocks = get_stock_data(db, symbol, limit=365)

    if not stocks:
        raise HTTPException(404, "No data")

    result = StockSummary(
        symbol=symbol,
        week_52_high=max(s["high"] for s in stocks),
        week_52_low=min(s["low"] for s in stocks),
        average_close=round(
            sum(s["close"] for s in stocks) / len(stocks), 2
        )
    )

    return success_response(
        message="Summary fetched successfully",
        data=result
    )


# =========================================================
# Compare
# =========================================================
@router.get(
    "/compare",
    response_model=SuccessResponse
)
def compare(
    symbol1: str,
    symbol2: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    perf1 = get_performance(db, symbol1, days)
    perf2 = get_performance(db, symbol2, days)

    if not perf1 or not perf2:
        raise HTTPException(404, "Performance data missing")

    return1 = perf1.get("return_pct", 0)
    return2 = perf2.get("return_pct", 0)

    if return1 > return2:
        winner = symbol1
    elif return2 > return1:
        winner = symbol2
    else:
        winner = "tie"

    insight = {
        "summary": (
            f"{winner} outperformed over {days} days"
            if winner != "tie"
            else f"Both stocks performed equally over {days} days"
        ),
        "recommendation": (
            winner if winner != "tie" else "No clear winner"
        )
    }

    result = {
        "symbol1": symbol1,
        "symbol2": symbol2,
        "period_days": days,
        "performance_1": perf1,
        "performance_2": perf2,
        "better_performer": winner,
        "return_difference": round(abs(return1 - return2), 2),
        "insight": insight
    }

    return success_response(
        message="Stock comparison analysis generated",
        data=result
    )


# =========================================================
# Follow Stock
# =========================================================
@router.post(
    "/follow/{symbol}",
    response_model=SuccessResponse
)
def follow(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = follow_stock(db, current_user.id, symbol)

    return success_response(message=result["message"])


# =========================================================
# Unfollow Stock
# =========================================================
@router.delete(
    "/unfollow/{symbol}",
    response_model=SuccessResponse
)
def unfollow(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = unfollow_stock(db, current_user.id, symbol)

    return success_response(message=result["message"])


# =========================================================
# User Stocks
# =========================================================
@router.get(
    "/my-stocks",
    response_model=SuccessResponse
)
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
@router.get(
    "/top-movers",
    response_model=SuccessResponse
)
def top_movers(db: Session = Depends(get_db)):
    result = get_top_movers(db)

    return success_response(
        message="Top movers fetched successfully",
        data=result
    )


# =========================================================
# Risk Analysis
# =========================================================
@router.get(
    "/risk/{symbol}",
    response_model=SuccessResponse
)
def risk(symbol: str, db: Session = Depends(get_db)):
    result = get_risk_analysis(db, symbol)

    return success_response(
        message="Risk analysis fetched successfully",
        data=result
    )


# =========================================================
# Performance
# =========================================================
@router.get(
    "/performance/{symbol}",
    response_model=SuccessResponse
)
def performance(symbol: str, days: int = 30, db: Session = Depends(get_db)):
    result = get_performance(db, symbol, days)

    return success_response(
        message="Performance fetched successfully",
        data=result
    )

# =========================================================
# Prediction
# =========================================================
@router.get(
    "/predict/{symbol}",
    response_model=SuccessResponse
)
def predict(symbol: str, db: Session = Depends(get_db)):
    result = get_prediction(db, symbol)

    return success_response(
        message="Prediction fetched successfully",
        data=result
    )
    