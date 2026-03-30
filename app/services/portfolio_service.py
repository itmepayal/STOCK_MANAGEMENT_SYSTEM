from sqlalchemy.orm import Session
from app.models.portfolio import Portfolio
from app.models.company import Company
from app.models.stock import StockData  

# ============================
# Add to Portfolio
# ============================
def add_to_portfolio(db: Session, user_id: int, symbol: str, quantity: int, buy_price: float):
    company = db.query(Company).filter(Company.symbol == symbol).first()

    if not company:
        return {"error": "Company not found"}

    portfolio = Portfolio(
        user_id=user_id,
        company_id=company.id,
        quantity=quantity,
        buy_price=buy_price
    )

    db.add(portfolio)
    db.commit()

    return {"message": "Stock added to portfolio"}


# ============================
# Get Portfolio
# ============================
def get_portfolio(db: Session, user_id: int):
    items = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()

    result = []

    for item in items:
        latest_stock = (
            db.query(StockData)
            .filter(StockData.company_id == item.company_id)
            .order_by(StockData.date.desc())
            .first()
        )

        current_price = latest_stock.close if latest_stock else 0

        invested = item.quantity * item.buy_price
        current_value = item.quantity * current_price
        profit_loss = current_value - invested

        profit_percent = (profit_loss / invested) * 100 if invested > 0 else 0

        status = "profit" if profit_loss > 0 else "loss"

        daily_change = latest_stock.daily_return or 0 if latest_stock else 0

        is_top = profit_percent > 20

        result.append({
            "symbol": item.company.symbol,
            "quantity": item.quantity,
            "buy_price": round(item.buy_price, 2),
            "current_price": round(current_price, 2),
            "invested": round(invested, 2),
            "current_value": round(current_value, 2),
            "profit_loss": round(profit_loss, 2),
            "profit_percent": round(profit_percent, 2),
            "status": status,
            "daily_change": round(daily_change, 2),
            "is_top": is_top
        })

    total_invested = sum(x["invested"] for x in result)
    total_value = sum(x["current_value"] for x in result)
    total_profit = total_value - total_invested

    total_profit_percent = (total_profit / total_invested) * 100 if total_invested > 0 else 0

    return {
        "stocks": result,
        "summary": {
            "total_invested": round(total_invested, 2),
            "total_value": round(total_value, 2),
            "total_profit": round(total_profit, 2),
            "total_profit_percent": round(total_profit_percent, 2)
        }
    }

