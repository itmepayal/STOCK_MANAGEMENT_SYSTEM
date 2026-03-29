from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.auth import hash_password, verify_password

def register_user(db: Session, username: str, email: str, password: str, role_id: int = None):
    hashed = hash_password(password)
    user = User(username=username, email=email, hashed_password=hashed, role_id=role_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

