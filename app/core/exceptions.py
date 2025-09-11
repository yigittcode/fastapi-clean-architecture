from typing import Union
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import structlog

logger = structlog.get_logger(__name__)


class CustomHTTPException(HTTPException):
    """Customized HTTP Exception"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        headers: dict = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class BusinessLogicError(Exception):
    """Custom exception for business logic errors"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class DatabaseError(Exception):
    """Custom exception for database errors"""
    
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP Exception handler"""
    logger.error(
        "HTTP Exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": request.url.path
            }
        }
    )


def _clean_validation_errors(errors):
    """Makes validation errors JSON-safe"""
    cleaned_errors = []
    
    for error in errors:
        cleaned_error = {
            "type": error.get("type"),
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "input": error.get("input")
        }
        
        # ctx içindeki ValueError'ları string'e çevir
        if "ctx" in error and error["ctx"]:
            cleaned_ctx = {}
            for key, value in error["ctx"].items():
                if isinstance(value, Exception):
                    cleaned_ctx[key] = str(value)
                else:
                    cleaned_ctx[key] = value
            cleaned_error["ctx"] = cleaned_ctx
        
        if "url" in error:
            cleaned_error["url"] = error["url"]
            
        cleaned_errors.append(cleaned_error)
    
    return cleaned_errors


async def validation_exception_handler(
    request: Request, 
    exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """Validation exception handler"""
    # Raw errors'ları temizle
    raw_errors = exc.errors()
    cleaned_errors = _clean_validation_errors(raw_errors)
    
    logger.error(
        "Validation error occurred",
        errors=[{k: v for k, v in err.items() if k != 'ctx'} for err in cleaned_errors],
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "validation_error",
                "message": "Validation failed",
                "details": cleaned_errors,
                "path": request.url.path
            }
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """SQLAlchemy exception handler"""
    logger.error(
        "Database error occurred",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True
    )
    
    # Integrity error (unique constraint vb.)
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": {
                    "type": "database_constraint_error",
                    "message": "Data integrity constraint violated",
                    "path": request.url.path
                }
            }
        )
    
    # Genel database hatası
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "database_error",
                "message": "Database operation failed",
                "path": request.url.path
            }
        }
    )


async def business_logic_exception_handler(request: Request, exc: BusinessLogicError) -> JSONResponse:
    """Business logic exception handler"""
    logger.warning(
        "Business logic error occurred",
        message=exc.message,
        error_code=exc.error_code,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "type": "business_logic_error",
                "message": exc.message,
                "error_code": exc.error_code,
                "path": request.url.path
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """General exception handler - last resort"""
    logger.error(
        "Unexpected error occurred",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "internal_server_error",
                "message": "An unexpected error occurred",
                "path": request.url.path
            }
        }
    )
