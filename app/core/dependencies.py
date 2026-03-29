# =========================================================
# Auth Dependencies
# =========================================================

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.auth import decode_token
from app.db.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer

# =========================================================
# OAuth2 Configuration
# =========================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# =========================================================
# Database Dependency
# =========================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
# Get Current User
# =========================================================
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# =========================================================
# Require Admin Role
# =========================================================
def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user
