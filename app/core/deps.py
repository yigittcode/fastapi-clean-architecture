from typing import Generator, Optional, Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_async_db
from .security import verify_token
from .logging import get_logger, LogContext
from .exceptions import CustomHTTPException
from ..models.user import User
import structlog

# Security scheme
security = HTTPBearer()

# Logger instance
logger = get_logger(__name__)


async def get_request_logger(request: Request) -> LogContext:
    """Create logger context for request"""
    request_logger = logger.bind(
        method=request.method,
        path=request.url.path,
        query_params=str(request.query_params),
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    return LogContext(request_logger)


async def get_current_user(
    db: AsyncSession = Depends(get_async_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    log_context: LogContext = Depends(get_request_logger)
) -> User:
    """Get current user"""
    log_context.info("Authenticating user")
    
    credentials_exception = CustomHTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        error_code="INVALID_CREDENTIALS"
    )
    
    try:
        username = verify_token(credentials.credentials)
        if username is None:
            log_context.warning("Invalid token provided")
            raise credentials_exception
        
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user is None:
            log_context.warning("User not found", username=username)
            raise credentials_exception
        
        log_context.info("User authenticated successfully", user_id=user.id, username=user.username)
        return user
        
    except Exception as e:
        log_context.error("Authentication failed", error=str(e))
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
    log_context: LogContext = Depends(get_request_logger)
) -> User:
    """Get active user"""
    if not current_user.is_active:
        log_context.warning("Inactive user attempted access", user_id=current_user.id)
        raise CustomHTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
            error_code="USER_INACTIVE"
        )
    
    log_context.debug("Active user verified", user_id=current_user.id)
    return current_user


async def get_superuser(
    current_user: User = Depends(get_current_active_user),
    log_context: LogContext = Depends(get_request_logger)
) -> User:
    """Superuser check"""
    if not current_user.is_superuser:
        log_context.warning("Non-superuser attempted admin access", user_id=current_user.id)
        raise CustomHTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
            error_code="INSUFFICIENT_PERMISSIONS"
        )
    
    log_context.debug("Superuser verified", user_id=current_user.id)
    return current_user


# Dependency injection type aliases
DatabaseDep = Annotated[AsyncSession, Depends(get_async_db)]  # Always async - modern approach
UserDep = Annotated[User, Depends(get_current_user)]
ActiveUserDep = Annotated[User, Depends(get_current_active_user)]
LoggerDep = Annotated[LogContext, Depends(get_request_logger)]
SuperuserDep = Annotated[User, Depends(get_superuser)]

