from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.user import UserRepository
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash


class UsersService:
    """Users business logic"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def get_users(
        self,
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        current_user: User = None
    ) -> List[User]:
        """Get all users (admin only)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return await self.user_repository.get_multi(db, skip=skip, limit=limit)
    
    async def get_user_by_id(self, db: AsyncSession, user_id: int, current_user: User) -> User:
        """Get user by ID"""
        # Users can only see their own profile, admins can see all
        if user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        user = await self.user_repository.get(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
    
    async def create_user(
        self,
        db: AsyncSession, 
        user_data: UserCreate, 
        current_user: User
    ) -> User:
        """Create new user (admin only)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Check if email exists
        existing_user = await self.user_repository.get_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Check if username exists
        existing_user = await self.user_repository.get_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        return await self.user_repository.create_user(db, user_data, hashed_password)
    
    async def update_user(
        self,
        db: AsyncSession, 
        user_id: int, 
        user_data: UserUpdate, 
        current_user: User
    ) -> User:
        """Update user"""
        # Users can only update their own profile, admins can update all
        if user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        user = await self.user_repository.get(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return await self.user_repository.update(db, user, user_data)
    
    async def delete_user(
        self,
        db: AsyncSession, 
        user_id: int, 
        current_user: User
    ) -> dict:
        """Delete user (admin only)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        user = await self.user_repository.delete(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "User deleted successfully"}


# Service instance removed - now using dependency injection through deps.py
