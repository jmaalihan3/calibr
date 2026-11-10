"""
Configuration module for application settings.

Loads configuration from environment variables with sensible defaults.
Uses python-dotenv to load .env file in development.

Security settings:
- SECRET_KEY: Used for session token signing (must be strong in production)
- CSRF_SECRET: Used for CSRF token generation
- SESSION_TIMEOUT_DAYS: How long sessions remain valid
"""

import os
from dotenv import load_dotenv
import secrets

# Load .env file if it exists (development)
load_dotenv()


class Config:
    """
    Application configuration loaded from environment variables.
    
    Attributes:
        DATABASE_URL: PostgreSQL connection string (None = use SQLite)
        SECRET_KEY: Secret for session signing (auto-generated if not set)
        CSRF_SECRET: Secret for CSRF tokens (auto-generated if not set)
        SESSION_TIMEOUT_DAYS: Session validity period (default 7 days)
        RATE_LIMIT_LOGIN: Login attempts per minute per IP
        RATE_LIMIT_REGISTER: Registration attempts per minute per IP
        ENVIRONMENT: development or production
    """
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Security - Generate random secrets if not provided (development only)
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        SECRET_KEY = secrets.token_urlsafe(32)
        if os.getenv("ENVIRONMENT") == "production":
            raise ValueError("SECRET_KEY must be set in production")
    
    CSRF_SECRET = os.getenv("CSRF_SECRET")
    if not CSRF_SECRET:
        CSRF_SECRET = secrets.token_urlsafe(32)
        if os.getenv("ENVIRONMENT") == "production":
            raise ValueError("CSRF_SECRET must be set in production")
    
    # Session configuration
    SESSION_TIMEOUT_DAYS = int(os.getenv("SESSION_TIMEOUT_DAYS", "7"))
    
    # Rate limiting
    RATE_LIMIT_LOGIN = int(os.getenv("RATE_LIMIT_LOGIN", "5"))
    RATE_LIMIT_REGISTER = int(os.getenv("RATE_LIMIT_REGISTER", "3"))
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return cls.ENVIRONMENT == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode."""
        return cls.ENVIRONMENT == "development"


# Export config instance
config = Config()
