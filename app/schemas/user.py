from typing import List
from pydantic import BaseModel
from datetime import datetime

# ============================
# UserResponse
# ============================
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    role: str

    class Config:
        from_attributes = True

# ============================
# Pagination Meta
# ============================
class Pagination(BaseModel):
    total: int
    skip: int
    limit: int

# ============================
# Users List Response
# ============================
class UsersListResponse(BaseModel):
    items: List["UserResponse"]
    pagination: Pagination
    