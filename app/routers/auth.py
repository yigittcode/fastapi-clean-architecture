from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..controllers.auth import AuthController
from ..schemas.auth import Token, LoginRequest
from ..schemas.user import UserCreate, User as UserSchema

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """User login - JSON format"""
    return await AuthController.login(login_data, db)


@router.post("/login/form", response_model=Token)
async def login_for_access_token_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """User login - Form format (OAuth2 compatible)"""
    login_data = LoginRequest(username=form_data.username, password=form_data.password)
    return await AuthController.login(login_data, db)


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Register new user"""
    return await AuthController.register(user, db)