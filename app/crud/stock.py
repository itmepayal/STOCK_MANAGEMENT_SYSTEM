from sqlalchemy.orm import Session
from app.models.stock_data import StockData

def create_stock(db: Session, company_id: int, date, open, high, low, close, volume=None):
    stock = StockData(
        company_id=company_id, date=date, open=open, high=high, low=low,
        close=close, volume=volume
    )
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock

def get_stocks_by_company(db: Session, company_id: int):
    return db.query(StockData).filter(StockData.company_id == company_id).all()
