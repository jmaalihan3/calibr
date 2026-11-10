"""
Authentication utilities and dependencies.

Provides:
- Password hashing with Argon2id (OWASP recommended)
- Session token generation and validation
- CSRF token generation and validation
- FastAPI dependencies for authentication
- Rate limiting for auth endpoints

Security:
- Never stores plaintext passwords
- Uses cryptographically secure random tokens
- Implements timing-safe comparisons
- Session tokens are hashed before storage
"""

import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import Request, HTTPException, status, Cookie, Header
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash
import time

from app.config import config


# Argon2id password hasher (OWASP recommended parameters)
ph = PasswordHasher(
    time_cost=2,        # Number of iterations
    memory_cost=65536,  # Memory usage in KiB (64 MB)
    parallelism=4,      # Number of parallel threads
    hash_len=32,        # Length of hash in bytes
    salt_len=16         # Length of salt in bytes
)


# Rate limiting storage (in-memory, simple implementation)
# Format: {ip_address: {endpoint: [(timestamp, count), ...]}}
_rate_limit_store: Dict[str, Dict[str, list]] = {}


def hash_password(password: str) -> str:
    """
    Hash password using Argon2id.
    
    Args:
        password: Plaintext password
    
    Returns:
        Argon2id hash string (includes salt and parameters)
    
    Example:
        >>> hash_password("MySecurePass123!")
        '$argon2id$v=19$m=65536,t=2,p=4$...'
    """
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify password against Argon2id hash.
    
    Uses timing-safe comparison to prevent timing attacks.
    
    Args:
        password: Plaintext password to verify
        password_hash: Stored Argon2id hash
    
    Returns:
        True if password matches, False otherwise
    
    Note: Automatically rehashes if parameters changed (future-proof)
    """
    try:
        ph.verify(password_hash, password)
        
        # Check if hash needs rehashing (parameters updated)
        if ph.check_needs_rehash(password_hash):
            # Note: Caller should update stored hash
            # This is handled in the login endpoint
            pass
        
        return True
    except (VerifyMismatchError, VerificationError, InvalidHash):
        return False


def generate_session_token() -> str:
    """
    Generate cryptographically secure session token.
    
    Returns:
        URL-safe random token (32 bytes = 43 characters base64)
    
    Example:
        >>> generate_session_token()
        'xB3yZ9kQ2mN5jR7pL1wD4vF6hK8tA0cE2gJ5nM7qS9u'
    """
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """
    Hash session token for database storage.
    
    Uses SHA-256 for speed (tokens are already cryptographically random).
    
    Args:
        token: Session token to hash
    
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(token.encode()).hexdigest()


def generate_csrf_token(session_id: str) -> str:
    """
    Generate CSRF token using HMAC (Synchronizer Token Pattern).
    
    Token is tied to session ID to prevent token fixation.
    
    Args:
        session_id: User's session ID
    
    Returns:
        HMAC-based CSRF token
    """
    message = f"{session_id}:{int(time.time())}"
    signature = hmac.new(
        config.CSRF_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{message}:{signature}"


def verify_csrf_token(csrf_token: str, session_id: str, max_age_seconds: int = 3600) -> bool:
    """
    Verify CSRF token.
    
    Args:
        csrf_token: Token from request header
        session_id: Current session ID
        max_age_seconds: Maximum token age (default 1 hour)
    
    Returns:
        True if token is valid, False otherwise
    """
    try:
        parts = csrf_token.split(':')
        if len(parts) != 3:
            return False
        
        token_session_id, timestamp_str, signature = parts
        
        # Verify session ID matches
        if token_session_id != session_id:
            return False
        
        # Verify timestamp not too old
        timestamp = int(timestamp_str)
        if time.time() - timestamp > max_age_seconds:
            return False
        
        # Verify HMAC signature
        message = f"{token_session_id}:{timestamp_str}"
        expected_signature = hmac.new(
            config.CSRF_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Timing-safe comparison
        return hmac.compare_digest(signature, expected_signature)
    except (ValueError, IndexError):
        return False


def check_rate_limit(ip_address: str, endpoint: str, max_requests: int, window_seconds: int = 60) -> bool:
    """
    Check if request exceeds rate limit.
    
    Simple in-memory implementation (resets on server restart).
    For production with multiple instances, use Redis or similar.
    
    Args:
        ip_address: Client IP address
        endpoint: Endpoint identifier (e.g., "login", "register")
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds (default 60)
    
    Returns:
        True if under limit, False if exceeded
    """
    now = time.time()
    
    # Initialize storage for this IP if needed
    if ip_address not in _rate_limit_store:
        _rate_limit_store[ip_address] = {}
    
    if endpoint not in _rate_limit_store[ip_address]:
        _rate_limit_store[ip_address][endpoint] = []
    
    # Clean old entries
    requests = _rate_limit_store[ip_address][endpoint]
    requests[:] = [ts for ts in requests if now - ts < window_seconds]
    
    # Check limit
    if len(requests) >= max_requests:
        return False
    
    # Record this request
    requests.append(now)
    return True


def rate_limit(endpoint: str, max_requests: int):
    """
    Dependency factory for rate limiting.
    
    Usage:
        @router.post("/login", dependencies=[Depends(rate_limit("login", 5))])
    
    Args:
        endpoint: Endpoint identifier
        max_requests: Maximum requests per minute
    
    Returns:
        FastAPI dependency function
    """
    async def dependency(request: Request):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not check_rate_limit(client_ip, endpoint, max_requests):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {max_requests} requests per minute."
            )
    
    return dependency


async def get_current_user_optional(
    request: Request,
    session_token: Optional[str] = Cookie(None, alias="session_token")
) -> Optional[Dict]:
    """
    Get current user from session (optional).
    
    Returns user data if authenticated, None if not.
    Does not raise exception if unauthenticated.
    
    Args:
        request: FastAPI request object
        session_token: Session token from cookie
    
    Returns:
        User dict if authenticated, None otherwise
    """
    if not session_token:
        return None
    
    # Import here to avoid circular dependency
    from app import db
    
    # Validate session
    user_data = db.validate_session(session_token)
    return user_data


async def get_current_user(
    request: Request,
    session_token: Optional[str] = Cookie(None, alias="session_token")
) -> Dict:
    """
    Get current user from session (required).
    
    Raises 401 if not authenticated.
    Use as dependency for protected endpoints.
    
    Args:
        request: FastAPI request object
        session_token: Session token from cookie
    
    Returns:
        User dict with id, email, created_at
    
    Raises:
        HTTPException 401 if not authenticated
    
    Usage:
        @router.get("/protected")
        async def protected_route(user: Dict = Depends(get_current_user)):
            return {"message": f"Hello {user['email']}"}
    """
    user = await get_current_user_optional(request, session_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return user


async def verify_csrf(
    request: Request,
    csrf_token: Optional[str] = Header(None, alias="X-CSRF-Token"),
    session_token: Optional[str] = Cookie(None, alias="session_token")
):
    """
    Verify CSRF token for state-changing requests.
    
    Use as dependency for POST/PUT/DELETE endpoints that modify data.
    
    Args:
        request: FastAPI request object
        csrf_token: CSRF token from request header
        session_token: Session token from cookie
    
    Raises:
        HTTPException 403 if CSRF token invalid or missing
    
    Usage:
        @router.post("/action", dependencies=[Depends(verify_csrf)])
        async def action(user: Dict = Depends(get_current_user)):
            # CSRF verified, proceed
            pass
    """
    # CSRF protection only for authenticated requests
    if not session_token:
        return
    
    if not csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token required"
        )
    
    # Import here to avoid circular dependency
    from app import db
    
    # Get session to verify token
    session = db.get_session_by_token(session_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    if not verify_csrf_token(csrf_token, session['id']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )
