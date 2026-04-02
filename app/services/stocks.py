# =========================================================
# Stock Services
# =========================================================
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
import logging
import json

from app.models import Company, StockData, UserStock
from app.core import redis_client

# =========================================================
# Logger
# =========================================================
logger = logging.getLogger(__name__)

# =========================================================
# Redis Configuration
# =========================================================
CACHE_TTL = 60

# =========================================================
# Get Stock Data Service 
# =========================================================
def get_stock_data(db: Session, symbol: str, limit: int = 30):
    cache_key = f"stock:{symbol}:{limit}"

    try:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.info(f"Cache HIT for {symbol}")
                return json.loads(cached_data)
        except Exception as redis_error:
            logger.warning(f"Redis GET error: {str(redis_error)}")

        logger.info(f"Cache MISS for {symbol}")

        company = db.query(Company).filter(Company.symbol == symbol).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

        stock_data = (
            db.query(StockData)
            .filter(StockData.company_id == company.id)
            .order_by(StockData.date.desc())
            .limit(limit)
            .all()
        )

        result = [
            {
                "date": str(s.date),
                "open": s.open,
                "high": s.high,
                "low": s.low,
                "close": s.close,
                "volume": s.volume
            }
            for s in stock_data
        ]

        try:
            redis_client.setex(cache_key, CACHE_TTL, json.dumps(result))
        except Exception as redis_error:
            logger.warning(f"Redis SET error: {str(redis_error)}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_stock_data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch stock data"
        )


# =========================================================
# Follow Stock Service 
# =========================================================
def follow_stock(db: Session, user_id: int, symbol: str):
    try:
        company = db.query(Company).filter(Company.symbol == symbol).first()

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

        existing_follow = (
            db.query(UserStock)
            .filter(
                UserStock.user_id == user_id,
                UserStock.company_id == company.id
            )
            .first()
        )

        if existing_follow:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already following this stock"
            )

        follow = UserStock(user_id=user_id, company_id=company.id)
        db.add(follow)
        db.commit()

        logger.info(f"User {user_id} followed {symbol}")

        return {"message": "Followed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()  
        logger.error(f"Error in follow_stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to follow stock"
        )


# =========================================================
# Unfollow Stock Service 
# =========================================================
def unfollow_stock(db: Session, user_id: int, symbol: str):
    try:
        company = db.query(Company).filter(Company.symbol == symbol).first()

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

        follow = (
            db.query(UserStock)
            .filter(
                UserStock.user_id == user_id,
                UserStock.company_id == company.id
            )
            .first()
        )

        if not follow:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock not followed"
            )

        db.delete(follow)
        db.commit()

        logger.info(f"User {user_id} unfollowed {symbol}")

        return {"message": "Unfollowed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error in unfollow_stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unfollow stock"
        )


# =========================================================
# Get User Followed Stocks Service 
# =========================================================
def get_user_stocks(db: Session, user_id: int, skip: int = 0, limit: int = 10):

    try:
        query = db.query(UserStock).filter(UserStock.user_id == user_id)

        total = query.count()

        follows = (
            query
            .options(joinedload(UserStock.company)) 
            .offset(skip)
            .limit(limit)
            .all()
        )

        result = [
            {"symbol": follow.company.symbol}
            for follow in follows
        ]

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": result
        }

    except Exception as e:
        logger.error(f"Error in get_user_stocks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch followed stocks"
        )

# =========================================================
# Top Movers Service
# =========================================================
def get_top_movers(db: Session):
    companies = db.query(Company).all()
    result = []

    for company in companies:
        latest = (
            db.query(StockData)
            .filter(StockData.company_id == company.id)
            .order_by(StockData.date.desc())
            .first()
        )

        if not latest or latest.daily_return is None:
            continue

        result.append({
            "symbol": company.symbol,
            "daily_return": latest.daily_return
        })

    return {
        "top_gainers": sorted(result, key=lambda x: x["daily_return"], reverse=True)[:5],
        "top_losers": sorted(result, key=lambda x: x["daily_return"])[:5]
    }

# =========================================================
# Risk Service
# =========================================================
def get_risk_analysis(db: Session, symbol: str):
    stocks = get_stock_data(db, symbol)

    if not stocks:
        raise HTTPException(404, "No data")

    volatilities = []

    for s in stocks:
        if s["open"] != 0:
            volatility = (s["high"] - s["low"]) / s["open"]
            volatilities.append(volatility)

    if not volatilities:
        raise HTTPException(400, "Not enough data")

    avg_volatility = sum(volatilities) / len(volatilities)

    return {
        "symbol": symbol,
        "risk_score": round(avg_volatility * 100, 2),
        "risk_level": "HIGH" if avg_volatility > 0.02 else "LOW"
    }   

# =========================================================
# Performance Service
# =========================================================
def get_performance(db: Session, symbol: str, days: int = 30):
    stocks = get_stock_data(db, symbol, limit=days)

    if not stocks or len(stocks) < 2:
        return None

    start_price = stocks[-1]["close"]
    end_price = stocks[0]["close"]

    change = end_price - start_price
    return_pct = (change / start_price) * 100

    return {
        "start_price": start_price,
        "end_price": end_price,
        "absolute_change": round(change, 2),
        "return_pct": round(return_pct, 2),
        "trend": "up" if change > 0 else "down"
    }

# =========================================================
# Prediction Service
# =========================================================
def get_prediction(db: Session, symbol: str):
    stocks = get_stock_data(db, symbol, limit=30)

    if not stocks:
        raise HTTPException(404, "No data")

    closes = [s["close"] for s in reversed(stocks)]

    avg_change = sum(
        closes[i] - closes[i - 1]
        for i in range(1, len(closes))
    ) / (len(closes) - 1)

    predicted_price = closes[-1] + avg_change

    return {
        "symbol": symbol,
        "current_price": closes[-1],
        "predicted_price": round(predicted_price, 2),
        "trend": "UP" if avg_change > 0 else "DOWN"
    }
    