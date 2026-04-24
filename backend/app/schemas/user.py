from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    status: str = "active"
    project_id: str

class UserCreate(UserBase):
    supabase_user_id: UUID

class UserResponse(UserBase):
    id: UUID
    supabase_user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
