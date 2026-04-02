# =========================================================
# Authentication Utilities
# =========================================================
import hashlib
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from typing import Optional

from app.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

# =========================================================
# Password Hashing Configuration
# =========================================================
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

# =========================================================
# Hash Password
# =========================================================
def hash_password(password: str) -> str:
    hashed = hashlib.sha256(password.encode()).hexdigest()    
    return pwd_context.hash(hashed)


# =========================================================
# Verify Password
# =========================================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    hashed = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(hashed, hashed_password)

# =========================================================
# Internal Token Generator
# =========================================================
def _generate_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()

    now = datetime.utcnow()

    to_encode.update({
        "exp": now + expires_delta,  
        "iat": now                  
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# =========================================================
# Create Access Token
# =========================================================
def create_access_token(data: dict) -> str:
    return _generate_token(
        data,
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

# =========================================================
# Create Refresh Token
# =========================================================
def create_refresh_token(data: dict) -> str:
    return _generate_token(
        data,
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

# =========================================================
# Decode Token
# =========================================================
def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except ExpiredSignatureError:
        return None

    except JWTError:
        return None