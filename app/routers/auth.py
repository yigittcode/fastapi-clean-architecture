from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from ..core.deps import DatabaseDep, AuthServiceDep
from ..schemas.auth import Token, LoginRequest
from ..schemas.user import UserCreate, User as UserSchema

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    login_data: LoginRequest,
    db: DatabaseDep,
    auth_service: AuthServiceDep
):
    """User login - JSON format"""
    return await auth_service.login(login_data, db)


@router.post("/login/form", response_model=Token)
async def login_for_access_token_form(
    db: DatabaseDep,
    auth_service: AuthServiceDep,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """User login - Form format (OAuth2 compatible)"""
    login_data = LoginRequest(username=form_data.username, password=form_data.password)
    return await auth_service.login(login_data, db)


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    db: DatabaseDep,
    auth_service: AuthServiceDep
):
    """Register new user"""
    return await auth_service.register(user, db)