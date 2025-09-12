from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from ..core.deps import AsyncDatabaseDep
from ..services.auth import AuthService
from ..schemas.auth import Token, LoginRequest
from ..schemas.user import UserCreate, User as UserSchema

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    login_data: LoginRequest,
    db: AsyncDatabaseDep
):
    """User login - JSON format"""
    return await AuthService.login(login_data, db)


@router.post("/login/form", response_model=Token)
async def login_for_access_token_form(
    db: AsyncDatabaseDep,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """User login - Form format (OAuth2 compatible)"""
    login_data = LoginRequest(username=form_data.username, password=form_data.password)
    return await AuthService.login(login_data, db)


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    db: AsyncDatabaseDep
):
    """Register new user"""
    return await AuthService.register(user, db)