from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
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
    volume = Column(Float, nullable=False)

    # Calculated metrics
    daily_return = Column(Float, default=0)
    ma_7d = Column(Float, default=0)
    ma_20d = Column(Float, default=0)
    ma_50d = Column(Float, default=0)
    week_52_high = Column(Float, default=0)
    week_52_low = Column(Float, default=0)
    volatility = Column(Float, default=0)

    # Relationship
    company = relationship("Company", back_populates="stocks")
    