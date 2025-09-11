from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """JWT token schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str

