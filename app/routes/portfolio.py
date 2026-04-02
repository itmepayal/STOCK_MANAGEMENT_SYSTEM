# =========================================================
# Portfolio Routes
# =========================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import get_db, get_current_user
from app.services import add_to_portfolio, get_portfolio
from app.models import User
from app.utils import success_response
from app.schemas import (
    PortfolioCreate,
    PortfolioResponse,
    SuccessResponse,
    MessageResponse
)
# =========================================================
# Router Configuration
# =========================================================
router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

# =========================================================
# Add to Portfolio
# =========================================================
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponse[MessageResponse]
)
def add_portfolio_item(
    payload: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = add_to_portfolio(
        db=db,
        user_id=current_user.id,
        symbol=payload.symbol,
        quantity=payload.quantity,
        buy_price=payload.buy_price
    )

    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to add stock")
        )

    return success_response(
        message="Stock added successfully",
        data={}
    )


# =========================================================
# Get User Portfolio
# =========================================================
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[PortfolioResponse]
)
def get_user_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    portfolio = get_portfolio(db, current_user.id)

    return success_response(
        message="Portfolio fetched successfully",
        data=portfolio
    )