from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .item import Item


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, description="Username must be 3-50 characters")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name maximum 100 characters")

    @validator('username')
    def validate_username(cls, v):
        """Username validation"""
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        """Full name validation"""
        if v and len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip() if v else v


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=6, description="Password minimum 6 characters")


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserInDB(UserBase):
    """User schema in database"""
    id: int
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDB):
    """User schema for responses"""
    pass


class UserWithItems(User):
    """User schema with items"""
    items: List['Item'] = []