# =========================================================
# Portfolio Services
# =========================================================
import logging
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models import Portfolio, Company, StockData

# =========================================================
# Logger
# =========================================================
logger = logging.getLogger(__name__)

# =========================================================
# Add to Portfolio
# =========================================================
def add_to_portfolio(
    db: Session,
    user_id: int,
    symbol: str,
    quantity: int,
    buy_price: float
):
    logger.info(f"Add to portfolio request user_id={user_id} symbol={symbol}")

    if quantity <= 0 or buy_price <= 0:
        logger.warning(f"Invalid input user_id={user_id} quantity={quantity} price={buy_price}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity and price must be positive"
        )

    company = db.query(Company).filter(Company.symbol == symbol).first()
    if not company:
        logger.warning(f"Company not found symbol={symbol}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    existing = db.query(Portfolio).filter(
        Portfolio.user_id == user_id,
        Portfolio.company_id == company.id
    ).first()

    try:
        if existing:
            logger.info(f"Updating existing portfolio user_id={user_id} company_id={company.id}")

            total_quantity = existing.quantity + quantity

            existing.buy_price = (
                (existing.buy_price * existing.quantity) +
                (buy_price * quantity)
            ) / total_quantity

            existing.quantity = total_quantity
            portfolio_item = existing

        else:
            logger.info(f"Creating new portfolio entry user_id={user_id} company_id={company.id}")

            portfolio_item = Portfolio(
                user_id=user_id,
                company_id=company.id,
                quantity=quantity,
                buy_price=buy_price
            )
            db.add(portfolio_item)

        db.commit()
        db.refresh(portfolio_item)

        logger.info(f"Portfolio updated successfully user_id={user_id} symbol={symbol}")

        return {
            "success": True,
            "data": portfolio_item
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Portfolio update failed user_id={user_id} error={str(e)}")
        raise

# =========================================================
# Get Portfolio
# =========================================================
def get_portfolio(db: Session, user_id: int):

    logger.info(f"Fetching portfolio for user_id={user_id}")

    try:
        items = (
            db.query(Portfolio)
            .options(joinedload(Portfolio.company)) 
            .filter(Portfolio.user_id == user_id)
            .all()
        )

        if not items:
            logger.info(f"No portfolio found for user_id={user_id}")
            return {
                "stocks": [],
                "summary": {
                    "total_invested": 0,
                    "total_value": 0,
                    "total_profit": 0,
                    "total_profit_percent": 0
                }
            }

        company_ids = [item.company_id for item in items]

        latest_prices = (
            db.query(StockData)
            .filter(StockData.company_id.in_(company_ids))
            .order_by(StockData.company_id, StockData.date.desc())
            .all()
        )

        latest_map = {}
        for stock in latest_prices:
            if stock.company_id not in latest_map:
                latest_map[stock.company_id] = stock

        result = []

        for item in items:
            latest_stock = latest_map.get(item.company_id)

            current_price = latest_stock.close if latest_stock else 0
            daily_change = latest_stock.daily_return if latest_stock else 0

            invested = item.quantity * item.buy_price
            current_value = item.quantity * current_price
            profit_loss = current_value - invested
            profit_percent = (profit_loss / invested) * 100 if invested > 0 else 0

            result.append({
                "symbol": item.company.symbol,
                "quantity": item.quantity,
                "buy_price": round(item.buy_price, 2),
                "current_price": round(current_price, 2),
                "invested": round(invested, 2),
                "current_value": round(current_value, 2),
                "profit_loss": round(profit_loss, 2),
                "profit_percent": round(profit_percent, 2),
                "status": "profit" if profit_loss > 0 else "loss",
                "daily_change": round(daily_change or 0, 2),
                "is_top": profit_percent > 20
            })

        total_invested = sum(x["invested"] for x in result)
        total_value = sum(x["current_value"] for x in result)
        total_profit = total_value - total_invested
        total_profit_percent = (total_profit / total_invested) * 100 if total_invested > 0 else 0

        logger.info(f"Portfolio fetched successfully user_id={user_id}")

        return {
            "stocks": result,
            "summary": {
                "total_invested": round(total_invested, 2),
                "total_value": round(total_value, 2),
                "total_profit": round(total_profit, 2),
                "total_profit_percent": round(total_profit_percent, 2)
            }
        }

    except Exception as e:
        logger.error(f"Failed to fetch portfolio user_id={user_id} error={str(e)}")
        raise
    