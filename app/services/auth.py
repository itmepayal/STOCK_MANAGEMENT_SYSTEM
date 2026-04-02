# =========================================================
# Auth Services
# =========================================================
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from app.models import User
from app.crud import register_user, authenticate_user
from app.utils import create_access_token, create_refresh_token, decode_token

# =========================================================
# Logger
# =========================================================
logger = logging.getLogger(__name__)

# =========================================================
# Register Service
# =========================================================
def register_service(db: Session, username: str, email: str, password: str):
    logger.info(f"Register attempt for email={email}")

    try:
        user = register_user(db, username, email, password)
        logger.info(f"User registered successfully id={user.id}")
        return user

    except Exception as e:
        logger.error(f"Registration failed for email={email} error={str(e)}")
        raise


# =========================================================
# Login Service
# =========================================================
def login_service(db: Session, email: str, password: str):
    logger.info(f"Login attempt for email={email}")

    user = authenticate_user(db, email, password)

    if not user:
        logger.warning(f"Invalid login attempt for email={email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    try:
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        user.refresh_token = refresh_token
        db.commit()

        logger.info(f"User login successful id={user.id}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user 
        }

    except Exception as e:
        logger.error(f"Login failed for email={email} error={str(e)}")
        raise


# =========================================================
# Refresh Service
# =========================================================
def refresh_service(db: Session, refresh_token: str):
    logger.info("Refresh token request received")

    payload = decode_token(refresh_token)

    if not payload:
        logger.warning("Invalid refresh token (decode failed)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")

    if not user_id:
        logger.warning("Invalid token payload (missing sub)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user or user.refresh_token != refresh_token:
        logger.warning(f"Refresh token mismatch for user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    try:
        new_access_token = create_access_token({"sub": str(user.id)})
        new_refresh_token = create_refresh_token({"sub": str(user.id)})

        user.refresh_token = new_refresh_token
        db.commit()

        logger.info(f"Token refreshed successfully user_id={user.id}")

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except Exception as e:
        logger.error(f"Token refresh failed user_id={user_id} error={str(e)}")
        raise


# =========================================================
# Logout Service
# =========================================================
def logout_service(db: Session, user: User):
    logger.info(f"Logout request for user_id={user.id}")

    try:
        user.refresh_token = None
        db.commit()

        logger.info(f"User logged out successfully user_id={user.id}")
        return True

    except Exception as e:
        logger.error(f"Logout failed user_id={user.id} error={str(e)}")
        raise


# =========================================================
# Get Users Service
# =========================================================
def get_users_service(db: Session, skip: int = 0, limit: int = 10):
    logger.info(f"Fetching users skip={skip} limit={limit}")

    try:
        users = db.query(User).offset(skip).limit(limit).all()
        total = db.query(User).count()

        logger.info(f"Fetched {len(users)} users out of total={total}")

        return users, total

    except Exception as e:
        logger.error(f"Failed to fetch users error={str(e)}")
        raise
    