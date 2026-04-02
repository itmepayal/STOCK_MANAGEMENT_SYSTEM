from pydantic import BaseModel, Field
from typing import List, Optional

# ============================
# Create Portfolio 
# ============================
class PortfolioCreate(BaseModel):
    symbol: str = Field(..., example="RELIANCE.NS")
    quantity: int = Field(..., gt=0, example=10)
    buy_price: float = Field(..., gt=0, example=2500.0)

# ============================
# Single Stock Response
# ============================
class PortfolioStock(BaseModel):
    symbol: str
    quantity: int
    buy_price: float
    current_price: float
    invested: float
    current_value: float
    profit_loss: float
    profit_percent: float
    status: str
    daily_change: float
    is_top: bool

# ============================
# Portfolio Summary
# ============================
class PortfolioSummary(BaseModel):
    total_invested: float
    total_value: float
    total_profit: float
    total_profit_percent: float

# ============================
# Full Portfolio Response
# ============================
class PortfolioResponse(BaseModel):
    stocks: List[PortfolioStock]
    summary: PortfolioSummary