from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class ItemBase(BaseModel):
    """Base item schema"""
    title: str = Field(..., min_length=1, max_length=200, description="Title must be 1-200 characters")
    description: Optional[str] = Field(None, max_length=1000, description="Description maximum 1000 characters")
    is_active: bool = True

    @validator('title')
    def validate_title(cls, v):
        """Title validasyonu"""
        v = v.strip()
        if len(v) < 1:
            raise ValueError('Title cannot be empty')
        if len(v) > 200:
            raise ValueError('Title cannot be longer than 200 characters')
        return v

    @validator('description')
    def validate_description(cls, v):
        """Description validasyonu"""
        if v:
            v = v.strip()
            if len(v) > 1000:
                raise ValueError('Description cannot be longer than 1000 characters')
            return v if v else None
        return v


class ItemCreate(ItemBase):
    """Item creation schema"""
    pass


class ItemUpdate(BaseModel):
    """Item update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ItemInDB(ItemBase):
    """Item schema from database"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Item(ItemInDB):
    """Item response schema"""
    pass


class ItemWithOwner(ItemInDB):
    """Item with owner information - only when explicitly requested"""
    owner_username: Optional[str] = None
    owner_email: Optional[str] = None
