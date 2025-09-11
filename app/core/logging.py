import logging
import sys
import os
from pathlib import Path
from typing import Any, Dict
import structlog
from rich.console import Console
from rich.logging import RichHandler
from logging.handlers import RotatingFileHandler
from .config import settings


def setup_logging() -> None:
    """Structured logging configuration"""
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Rich console for beautiful output
    console = Console()
    
    # Setup handlers
    handlers = [
        RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=settings.debug
        )
    ]
    
    # Add file handlers
    # Main log file
    file_handler = RotatingFileHandler(
        logs_dir / "app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    handlers.append(file_handler)
    
    # Error log file
    error_handler = RotatingFileHandler(
        logs_dir / "error.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'
    ))
    handlers.append(error_handler)
    
    # Configure standard library logging
    logging.basicConfig(
        level=logging.INFO if not settings.debug else logging.DEBUG,
        format="%(message)s",
        datefmt="[%X]",
        handlers=handlers
    )
    
    # Silence watchfiles logger - prevent infinite loop
    logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
    
    # Configure structlog with cleaner formatting
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="ISO"),
            # Use simple key-value renderer for cleaner logs
            structlog.processors.KeyValueRenderer(key_order=['timestamp', 'level', 'event'], sort_keys=False)
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.INFO if not settings.debug else logging.DEBUG
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """Get structured logger"""
    return structlog.get_logger(name)


# Special context manager for request logging
class LogContext:
    """Logging for request context"""
    
    def __init__(self, logger: structlog.BoundLogger):
        self.logger = logger
    
    def bind(self, **kwargs: Any) -> structlog.BoundLogger:
        """Add context"""
        return self.logger.bind(**kwargs)
    
    def info(self, event: str, **kwargs: Any) -> None:
        """Info log"""
        self.logger.info(event, **kwargs)
    
    def error(self, event: str, **kwargs: Any) -> None:
        """Error log"""
        self.logger.error(event, **kwargs)
    
    def warning(self, event: str, **kwargs: Any) -> None:
        """Warning log"""
        self.logger.warning(event, **kwargs)
    
    def debug(self, event: str, **kwargs: Any) -> None:
        """Debug log"""
        self.logger.debug(event, **kwargs)
