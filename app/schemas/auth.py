from pydantic import BaseModel, EmailStr, Field
from .user import UserResponse

# ============================
# Register Request
# ============================
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="Payal")
    email: EmailStr = Field(..., example="itme.payalyadav@gmail.com")
    password: str = Field(..., min_length=6, example="strongpassword123")

# ============================
# Login Request
# ============================
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="itme.payalyadav@gmail.com")
    password: str = Field(..., example="strongpassword123")

# ============================
# Refresh Token Request
# ============================
class RefreshRequest(BaseModel):
    refresh_token: str

# ============================
# Auth Response (OPTIONAL)
# ============================
class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse

# ============================
# Refresh Response
# ============================
class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
# ============================
# Message Response
# ============================
class MessageResponse(BaseModel):
    message: str
    