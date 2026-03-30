# =========================================================
# Auth Services
# =========================================================

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.crud.auth import register_user, authenticate_user
from app.utils.auth import create_access_token, create_refresh_token, decode_token


# =========================================================
# Register Service
# =========================================================
def register_service(db: Session, username: str, email: str, password: str):
    user = register_user(db, username, email, password)
    return user


# =========================================================
# Login Service
# =========================================================
def login_service(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    user.refresh_token = refresh_token
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user 
    }


# =========================================================
# Refresh Service
# =========================================================
def refresh_service(db: Session, refresh_token: str):
    payload = decode_token(refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user or user.refresh_token != refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    new_access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    user.refresh_token = new_refresh_token
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


# =========================================================
# Logout Service
# =========================================================
def logout_service(db: Session, user: User):
    user.refresh_token = None
    db.commit()

    return True


# =========================================================
# Get Users Service
# =========================================================
def get_users_service(db: Session, skip: int = 0, limit: int = 10):
    users = db.query(User).offset(skip).limit(limit).all()
    total = db.query(User).count()
    return users, total
