import hashlib
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
import os
from typing import Optional
from app.config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

# -----------------------------
# Password Hashing
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(hashed)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    hashed = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(hashed, hashed_password)

# -----------------------------
# JWT Utility Functions
# -----------------------------
def _generate_token(data: dict, expires_delta: timedelta) -> str:
    """
    Generate a JWT token with expiration.
    """
    to_encode = data.copy()
    now = datetime.utcnow()
    to_encode.update({
        "exp": now + expires_delta,
        "iat": now
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(data: dict) -> str:
    """
    Create a short-lived access token.
    """
    return _generate_token(data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

def create_refresh_token(data: dict) -> str:
    """
    Create a long-lived refresh token.
    """
    return _generate_token(data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

def decode_token(token: str) -> Optional[dict]:
    """
    Decode a JWT token and return its payload.
    Returns None if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None
    