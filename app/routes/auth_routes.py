# =========================================================
# FastAPI Authentication Router & Dependencies
# =========================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest
from app.services.auth_service import (
    register_service,
    login_service,
    refresh_service,
    logout_service,
    get_users_service
)
from app.core.dependencies import get_db, get_current_user, require_admin
from app.models.user import User

# =========================================================
# Router Configuration
# =========================================================
router = APIRouter(prefix="/auth", tags=["Authentication"])

# =========================================================
# Auth Endpoints
# =========================================================
@router.post("/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    return register_service(
        db,
        request.username,
        request.email,
        request.password
    )


@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    return login_service(db, request.email, request.password)


@router.post("/refresh")
def refresh(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):
    return refresh_service(db, request.refresh_token)


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return logout_service(db, current_user)


# =========================================================
# Get Users
# =========================================================
@router.get("/users")
def get_users(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(require_admin),  
    db: Session = Depends(get_db)
):
    return get_users_service(db, skip, limit)
