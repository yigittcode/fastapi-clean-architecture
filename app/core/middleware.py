import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import structlog

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/Response logging middleware"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Request ID oluştur
        request_id = str(uuid.uuid4())
        
        # Request başlangıç zamanı
        start_time = time.time()
        
        # Request bilgilerini logla
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        # Request ID'yi header'a ekle
        request.state.request_id = request_id
        
        try:
            # Response'ı al
            response = await call_next(request)
            
            # İşlem süresi
            process_time = time.time() - start_time
            
            # Response bilgilerini logla
            logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time=f"{process_time:.4f}s"
            )
            
            # Response header'a request ID ekle
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            return response
            
        except Exception as e:
            # Hata durumunda logla
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                error=str(e),
                process_time=f"{process_time:.4f}s",
                exc_info=True
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that adds security headers"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Güvenlik header'larını ekle
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # CSP - Swagger UI için CDN erişimi izin ver
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "img-src 'self' data: cdn.jsdelivr.net fastapi.tiangolo.com; "
            "font-src 'self' cdn.jsdelivr.net"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        return response


class RateLimitInfo:
    """Rate limiting bilgileri"""
    def __init__(self, requests: int = 0, window_start: float = None):
        self.requests = requests
        self.window_start = window_start or time.time()


# Basit in-memory rate limiter (production'da Redis kullanın)
rate_limit_storage: dict[str, RateLimitInfo] = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Basit rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # İzin verilen istek sayısı
        self.period = period  # Süre (saniye)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Client IP'sini al
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Rate limit kontrolü
        if client_ip in rate_limit_storage:
            rate_info = rate_limit_storage[client_ip]
            
            # Zaman penceresi sıfırlandı mı?
            if current_time - rate_info.window_start > self.period:
                rate_info.requests = 0
                rate_info.window_start = current_time
            
            # Limit aşıldı mı?
            if rate_info.requests >= self.calls:
                logger.warning(
                    "Rate limit exceeded",
                    client_ip=client_ip,
                    requests=rate_info.requests,
                    limit=self.calls
                )
                
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "type": "rate_limit_exceeded",
                            "message": "Too many requests",
                            "retry_after": int(self.period - (current_time - rate_info.window_start))
                        }
                    }
                )
            
            # İstek sayısını artır
            rate_info.requests += 1
        else:
            # İlk istek
            rate_limit_storage[client_ip] = RateLimitInfo(requests=1, window_start=current_time)
        
        response = await call_next(request)
        
        # Rate limit bilgilerini header'a ekle
        rate_info = rate_limit_storage[client_ip]
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.calls - rate_info.requests))
        response.headers["X-RateLimit-Reset"] = str(int(rate_info.window_start + self.period))
        
        return response
