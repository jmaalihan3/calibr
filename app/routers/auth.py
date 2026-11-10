"""
Authentication API endpoints.

Endpoints:
- POST /api/auth/register: Create new user account
- POST /api/auth/login: Authenticate and create session
- POST /api/auth/logout: Revoke session
- GET /api/auth/me: Get current user profile
- GET /api/auth/csrf-token: Get CSRF token for authenticated requests

Security:
- Passwords hashed with Argon2id
- Sessions via Secure, HttpOnly, SameSite cookies
- CSRF protection with Synchronizer Token Pattern
- Rate limiting on auth endpoints
"""

from fastapi import APIRouter, HTTPException, status, Response, Depends, Request, Cookie
from typing import Optional, Dict
from datetime import datetime, timedelta

from app.models import (
    RegisterRequest, 
    LoginRequest, 
    UserResponse, 
    LoginResponse, 
    MessageResponse,
    CSRFTokenResponse
)
from app.auth import (
    hash_password,
    verify_password,
    generate_session_token,
    hash_token,
    generate_csrf_token,
    rate_limit,
    get_current_user,
    get_current_user_optional,
    verify_csrf
)
from app.config import config
from app import db


router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("register", config.RATE_LIMIT_REGISTER))]
)
async def register(request: RegisterRequest):
    """
    Register a new user account.
    
    Request body:
        {
            "email": "user@example.com",
            "password": "SecurePass123!"
        }
    
    Password requirements:
    - At least 8 characters
    - Contains uppercase letter
    - Contains lowercase letter
    - Contains digit
    - Contains special character
    
    Response:
        {
            "message": "Registration successful",
            "detail": "Please log in with your credentials"
        }
    
    Status codes:
        201: Registration successful
        400: Invalid input or email already registered
        429: Rate limit exceeded
    
    Security:
    - Password is hashed with Argon2id before storage
    - Email uniqueness checked (case-insensitive)
    - Error message doesn't reveal if email exists
    """
    try:
        # Hash password
        password_hash = hash_password(request.password)
        
        # Create user
        user_id = db.create_user(request.email, password_hash)
        
        return MessageResponse(
            message="Registration successful",
            detail="Please log in with your credentials"
        )
    
    except ValueError as e:
        # Email already registered
        # Use generic error to avoid revealing user existence
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Please check your information and try again."
        )
    except Exception as e:
        # Log error for debugging (in production, use proper logging)
        print(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later."
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    dependencies=[Depends(rate_limit("login", config.RATE_LIMIT_LOGIN))]
)
async def login(request: LoginRequest, response: Response):
    """
    Authenticate user and create session.
    
    Request body:
        {
            "email": "user@example.com",
            "password": "SecurePass123!"
        }
    
    Response:
        {
            "user": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "created_at": "2026-11-09T17:30:00",
                "email_verified": false
            },
            "csrf_token": "session_id:timestamp:signature",
            "message": "Login successful"
        }
    
    Status codes:
        200: Login successful
        401: Invalid credentials
        429: Rate limit exceeded
    
    Security:
    - Session cookie set as Secure, HttpOnly, SameSite
    - CSRF token returned in response body
    - Generic error message doesn't reveal if email exists
    - Rate limited to prevent brute force
    """
    # Get user by email
    user = db.get_user_by_email(request.email)
    
    # Verify password
    if not user or not verify_password(request.password, user['password_hash']):
        # Generic error message to avoid revealing user existence
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    # Generate session token
    token = generate_session_token()
    token_hash_value = hash_token(token)
    
    # Calculate expiration
    expires_at = datetime.now() + timedelta(days=config.SESSION_TIMEOUT_DAYS)
    
    # Create session in database
    session_id = db.create_session(user['id'], token_hash_value, expires_at)
    
    # Generate CSRF token
    csrf_token = generate_csrf_token(session_id)
    
    # Set session cookie
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,  # Prevents JavaScript access
        secure=config.is_production(),  # HTTPS only in production
        samesite="lax",  # CSRF protection
        max_age=config.SESSION_TIMEOUT_DAYS * 24 * 60 * 60,  # Seconds
        path="/"
    )
    
    # Return user data and CSRF token
    user_response = UserResponse(
        id=str(user['id']),
        email=user['email'],
        created_at=user['created_at'] if isinstance(user['created_at'], datetime) else datetime.fromisoformat(user['created_at']),
        email_verified=user.get('email_verified', False)
    )
    
    return LoginResponse(
        user=user_response,
        csrf_token=csrf_token,
        message="Login successful"
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    dependencies=[Depends(verify_csrf)]
)
async def logout(
    response: Response,
    session_token: Optional[str] = Cookie(None, alias="session_token")
):
    """
    Logout user and revoke session.
    
    Request:
        - Requires session cookie
        - Requires CSRF token in X-CSRF-Token header
    
    Response:
        {
            "message": "Logout successful"
        }
    
    Status codes:
        200: Logout successful
        401: Not authenticated
        403: Invalid CSRF token
    
    Security:
    - CSRF protected (requires valid token)
    - Revokes session in database
    - Clears session cookie
    """
    if session_token:
        # Revoke session
        db.revoke_session(session_token)
    
    # Clear session cookie
    response.delete_cookie(
        key="session_token",
        path="/"
    )
    
    return MessageResponse(message="Logout successful")


@router.get(
    "/me",
    response_model=UserResponse
)
async def get_me(user: Dict = Depends(get_current_user)):
    """
    Get current user profile.
    
    Request:
        - Requires session cookie
    
    Response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "created_at": "2026-11-09T17:30:00",
            "email_verified": false
        }
    
    Status codes:
        200: Success
        401: Not authenticated
    
    Used by: Frontend to restore authentication state on page load
    """
    return UserResponse(
        id=str(user['id']),
        email=user['email'],
        created_at=user['created_at'] if isinstance(user['created_at'], datetime) else datetime.fromisoformat(str(user['created_at'])),
        email_verified=user.get('email_verified', False)
    )


@router.get(
    "/csrf-token",
    response_model=CSRFTokenResponse
)
async def get_csrf_token(
    session_token: Optional[str] = Cookie(None, alias="session_token")
):
    """
    Get CSRF token for authenticated requests.
    
    Request:
        - Requires session cookie
    
    Response:
        {
            "csrf_token": "session_id:timestamp:signature"
        }
    
    Status codes:
        200: Success
        401: Not authenticated
    
    Used by: Frontend to obtain CSRF token after page load
    """
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Get session
    session = db.get_session_by_token(session_token)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    # Generate CSRF token
    csrf_token = generate_csrf_token(session['id'])
    
    return CSRFTokenResponse(csrf_token=csrf_token)
