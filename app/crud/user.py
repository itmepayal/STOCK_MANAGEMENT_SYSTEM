# =========================================================
# User CRUD Operations
# Handles user creation, retrieval, and stock follow logic
# =========================================================

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import User
from app.models.user_stock import UserStock

# =========================================================
# Password Hashing Configuration
# =========================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =========================================================
# Create User
# =========================================================
def create_user(db: Session, username: str, email: str, password: str, role_id: int):
    hashed_password = pwd_context.hash(password)

    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role_id=role_id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# =========================================================
# Get User by Email
# =========================================================
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# =========================================================
# Follow Stock
# =========================================================
def follow_stock(db: Session, user_id: int, company_id: int):
    follow = UserStock(user_id=user_id, company_id=company_id)

    db.add(follow)
    db.commit()
    db.refresh(follow)

    return follow


# =========================================================
# Get Followed Stocks
# =========================================================
def get_user_followed_stocks(db: Session, user_id: int):
    return db.query(UserStock).filter(UserStock.user_id == user_id).all()