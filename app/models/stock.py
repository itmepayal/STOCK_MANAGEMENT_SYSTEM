from sqlalchemy import Column, Integer, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class StockData(Base):
    __tablename__ = "stock_data"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float)
    daily_return = Column(Float)
    ma_7d = Column(Float)
    week_52_high = Column(Float)
    week_52_low = Column(Float)
    volatility = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="stocks")
    