from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.security import verify_password, create_access_token, get_password_hash
from ..core.config import settings
from ..models.user import User
from ..schemas.auth import LoginRequest
from ..schemas.user import UserCreate
from ..repositories.auth import auth_repository


class AuthService:
    """Authentication business logic"""
    
    @staticmethod
    async def login(login_data: LoginRequest, db: AsyncSession) -> dict:
        """Handle user login"""
        user = await auth_repository.get_user_by_username(db, login_data.username)
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled",
            )
        
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    @staticmethod
    async def register(user_data: UserCreate, db: AsyncSession) -> User:
        """Handle user registration"""
        # Check if email exists
        existing_user = await auth_repository.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Check if username exists
        existing_user = await auth_repository.get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        return await auth_repository.create_user_with_hashed_password(db, user_data, hashed_password)
