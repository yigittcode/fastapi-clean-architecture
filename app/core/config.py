from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    app_name: str
    debug: bool
    version: str
    
    # Database
    database_url: str
    
    # Security
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    # Default Admin User
    admin_email: str
    admin_username: str
    admin_full_name: str
    admin_password: str
    
    model_config = {"env_file": ".env"}

settings = Settings()
