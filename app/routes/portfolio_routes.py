from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.services.portfolio_service import add_to_portfolio, get_portfolio, portfolio_chart

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.post("/")
def add(symbol: str, quantity: int, buy_price: float, db: Session = Depends(get_db)):
    return add_to_portfolio(db, USER_ID, symbol, quantity, buy_price)


@router.get("/")
def get(db: Session = Depends(get_db)):
    return get_portfolio(db, USER_ID)

