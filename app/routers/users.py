from typing import List
from fastapi import APIRouter, Depends, status
from ..core.deps import DatabaseDep, ActiveUserDep, SuperuserDep, LoggerDep, UsersServiceDep
from ..schemas.user import User as UserSchema, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: DatabaseDep,
    logger: LoggerDep,
    current_user: SuperuserDep,
    users_service: UsersServiceDep
):
    """Create new user (Admin only)"""
    logger.info("Creating new user", username=user.username)
    return await users_service.create_user(db, user, current_user)


@router.get("/", response_model=List[UserSchema])
async def read_users(
    db: DatabaseDep,
    logger: LoggerDep,
    current_user: SuperuserDep,
    users_service: UsersServiceDep,
    skip: int = 0,
    limit: int = 100
):
    """Get all users (Admin only)"""
    logger.info("Fetching users list", skip=skip, limit=limit)
    return await users_service.get_users(db, skip, limit, current_user)


@router.get("/me/", response_model=UserSchema)
async def read_users_me(
    db: DatabaseDep,
    logger: LoggerDep,
    current_user: ActiveUserDep
):
    """Get current user profile"""
    logger.info("Fetching current user profile", user_id=current_user.id)
    return current_user


@router.get("/{user_id}", response_model=UserSchema)
async def read_user(
    user_id: int,
    db: DatabaseDep,
    logger: LoggerDep,
    current_user: ActiveUserDep,
    users_service: UsersServiceDep
):
    """Get user by ID"""
    logger.info("Fetching user by ID", user_id=user_id)
    return await users_service.get_user_by_id(db, user_id, current_user)


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: DatabaseDep,
    logger: LoggerDep,
    current_user: ActiveUserDep,
    users_service: UsersServiceDep
):
    """Update user"""
    logger.info("Updating user", user_id=user_id)
    return await users_service.update_user(db, user_id, user_update, current_user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: DatabaseDep,
    logger: LoggerDep,
    current_user: SuperuserDep,
    users_service: UsersServiceDep
):
    """Delete user (Admin only)"""
    logger.info("Deleting user", user_id=user_id)
    return await users_service.delete_user(db, user_id, current_user)