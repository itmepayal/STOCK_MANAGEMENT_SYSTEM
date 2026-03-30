# =========================================================
# Authentication Router 
# =========================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest
from app.schemas.user import UserResponse
from app.services.auth_service import (
    register_service,
    login_service,
    refresh_service,
    logout_service,
    get_users_service
)
from app.core.dependencies import get_db, get_current_user, require_admin
from app.models.user import User
from app.utils.response import success_response

# =========================================================
# Router Configuration
# =========================================================
router = APIRouter(prefix="/auth", tags=["Authentication"])

# =========================================================
# Register
# =========================================================
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    user = register_service(
        db,
        request.username,
        request.email,
        request.password
    )

    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        role=user.role.name if user.role else None
    )

    return success_response(
        message="User registered successfully",
        data={"user": user_response}
    )

# =========================================================
# Login
# =========================================================
@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    result = login_service(db, request.email, request.password)

    user = result["user"]

    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        role=user.role.name if user.role else None
    )

    return success_response(
        message="Login successful",
        data={
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": result["token_type"],
            "user": user_response
        }
    )

# =========================================================
# Refresh token
# =========================================================
@router.post("/refresh")
def refresh(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):
    result = refresh_service(db, request.refresh_token)

    return success_response(
        message="Token refreshed successfully",
        data=result
    )

# =========================================================
# Logout
# =========================================================
@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logout_service(db, current_user)

    return success_response(
        message="Logged out successfully"
    )

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
    users, total = get_users_service(db, skip, limit)

    return success_response(
        message="Users fetched successfully",
        data={
            "items": [
                {
                    "id": u.id,
                    "username": u.username,
                    "email": u.email
                }
                for u in users
            ],
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    )