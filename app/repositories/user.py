from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """User repository with specialized queries"""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_active_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users"""
        result = await db.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_superusers(self, db: AsyncSession) -> List[User]:
        """Get all superusers"""
        result = await db.execute(select(User).where(User.is_superuser == True))
        return result.scalars().all()
    
    async def get_with_items(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user with their items loaded"""
        result = await db.execute(
            select(User)
            .options(selectinload(User.items))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_user(self, db: AsyncSession, user_data: UserCreate, hashed_password: str) -> User:
        """Create user with hashed password"""
        user_dict = user_data.dict()
        user_dict["hashed_password"] = hashed_password
        user_dict.pop("password", None)  # Remove plain password
        
        db_user = User(**user_dict)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    async def update_password(self, db: AsyncSession, user: User, hashed_password: str) -> User:
        """Update user password"""
        user.hashed_password = hashed_password
        await db.commit()
        await db.refresh(user)
        return user
    
    async def activate_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Activate a user"""
        user = await self.get(db, user_id)
        if user:
            user.is_active = True
            await db.commit()
            await db.refresh(user)
        return user
    
    async def deactivate_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Deactivate a user"""
        user = await self.get(db, user_id)
        if user:
            user.is_active = False
            await db.commit()
            await db.refresh(user)
        return user


# Singleton instance
user_repository = UserRepository()
