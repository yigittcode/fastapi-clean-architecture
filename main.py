from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from pydantic import ValidationError

from app.core.config import settings
from app.core.database import sync_engine, get_async_db
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    business_logic_exception_handler,
    general_exception_handler,
    BusinessLogicError,
    CustomHTTPException
)
from app.core.middleware import LoggingMiddleware, SecurityHeadersMiddleware, RateLimitMiddleware
from app.models import user, item  # Import models to create tables
from app.routers import auth, users, items
from app.core.security import get_password_hash
from app.models.user import User

# Setup logging
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Application startup initiated", version=settings.version, debug=settings.debug)
    
    # Create tables
    from app.core.database import Base
    Base.metadata.create_all(bind=sync_engine)
    
    # Create test user (development only)
    if settings.debug:
        try:
            from app.repositories.auth import auth_repository
            from app.schemas.user import UserCreate
            from app.core.database import AsyncSessionLocal
            
            async with AsyncSessionLocal() as db:
                # Check if admin user exists
                admin_user = await auth_repository.get_user_by_username(db, settings.admin_username)
                if not admin_user:
                    user_data = UserCreate(
                        email=settings.admin_email,
                        username=settings.admin_username,
                        full_name=settings.admin_full_name,
                        password=settings.admin_password
                    )
                    hashed_password = get_password_hash(settings.admin_password)
                    await auth_repository.create_user_with_hashed_password(db, user_data, hashed_password)
                    
                    # Make admin superuser
                    admin_user = await auth_repository.get_user_by_username(db, settings.admin_username)
                    admin_user.is_superuser = True
                    await db.commit()
                    
                    logger.info("Admin user created", username=settings.admin_username)
                    print(f"Admin user created: username={settings.admin_username}, password={settings.admin_password}")
                else:
                    logger.info("Admin user already exists")
        except Exception as e:
            logger.error("Failed to create admin user", error=str(e))
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Application shutdown")

# FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    description="Basic REST API for learning FastAPI - with Logging, DI and Exception Handling",
    lifespan=lifespan
)

# Exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(CustomHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(BusinessLogicError, business_logic_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Add middleware (order matters!)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)  # 100 requests/minute

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(items.router)

# Static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def root():
    """Main page"""
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to FastAPI Learning API!",
        "version": settings.version,
        "features": [
            "PostgreSQL Database",
            "JWT Authentication", 
            "Structured Logging",
            "Global Exception Handling",
            "Dependency Injection",
            "Rate Limiting",
            "Security Headers"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check"""
    logger.info("Health check accessed")
    
    # Database connection check
    try:
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.version,
        "database": db_status,
        "timestamp": "2024-01-01T00:00:00Z"  # This should be real timestamp
    }




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
