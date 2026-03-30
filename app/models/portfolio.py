from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))

    quantity = Column(Integer, nullable=False)
    buy_price = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company")
