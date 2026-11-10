"""
Pydantic models for request/response validation.

Models for:
- User registration and login
- Session management
- User profile data

All models include validation and documentation.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re


class RegisterRequest(BaseModel):
    """
    Request model for user registration.
    
    Validation:
    - Email must be valid format
    - Password must be at least 8 characters
    - Password must contain uppercase, lowercase, number, and special char
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets security requirements.
        
        Requirements:
        - At least 8 characters
        - Contains uppercase letter
        - Contains lowercase letter
        - Contains digit
        - Contains special character
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;/`~]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v


class LoginRequest(BaseModel):
    """
    Request model for user login.
    
    Fields:
    - email: User email address
    - password: User password (validated length only, not strength)
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, max_length=128, description="User password")


class UserResponse(BaseModel):
    """
    Response model for user profile data.
    
    Does NOT include password or sensitive data.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="User email address")
    created_at: datetime = Field(..., description="Account creation timestamp")
    email_verified: bool = Field(default=False, description="Email verification status")


class LoginResponse(BaseModel):
    """
    Response model for successful login.
    
    Includes:
    - User profile data
    - CSRF token for subsequent requests
    - Session cookie is set via Set-Cookie header (not in body)
    """
    user: UserResponse = Field(..., description="User profile data")
    csrf_token: str = Field(..., description="CSRF token for state-changing requests")
    message: str = Field(default="Login successful", description="Success message")


class MessageResponse(BaseModel):
    """
    Generic message response for simple endpoints.
    
    Used for:
    - Logout confirmation
    - Registration success
    - Error messages
    """
    message: str = Field(..., description="Response message")
    detail: Optional[str] = Field(None, description="Additional details")


class CSRFTokenResponse(BaseModel):
    """
    Response model for CSRF token endpoint.
    
    Used by frontend to obtain CSRF token for authenticated requests.
    """
    csrf_token: str = Field(..., description="CSRF token")
