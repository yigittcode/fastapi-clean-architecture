from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base import BaseRepository
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate


class AuthRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Authentication repository for user authentication operations"""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_user_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username for authentication"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email for authentication"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create_user_with_hashed_password(
        self, 
        db: AsyncSession, 
        user_data: UserCreate, 
        hashed_password: str
    ) -> User:
        """Create user with hashed password for registration"""
        user_dict = user_data.dict()
        user_dict["hashed_password"] = hashed_password
        user_dict.pop("password", None)  # Remove plain password
        
        db_user = User(
            email=user_dict["email"],
            username=user_dict["username"],
            full_name=user_dict.get("full_name"),
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user


# Singleton instance removed - now using dependency injection through deps.py
