"""
Tests for authentication utilities.

Tests:
- Password hashing and verification
- Session token generation and hashing
- CSRF token generation and verification
- Rate limiting
"""

import pytest
import time
from app.auth import (
    hash_password,
    verify_password,
    generate_session_token,
    hash_token,
    generate_csrf_token,
    verify_csrf_token,
    check_rate_limit,
    _rate_limit_store
)


def test_hash_password():
    """Test password hashing with Argon2id."""
    password = "SecurePass123!"
    hashed = hash_password(password)
    
    # Should start with Argon2id identifier
    assert hashed.startswith("$argon2id$")
    
    # Should be different from plaintext
    assert hashed != password
    
    # Hashing same password should produce different hash (random salt)
    hashed2 = hash_password(password)
    assert hashed != hashed2


def test_verify_password_success():
    """Test successful password verification."""
    password = "SecurePass123!"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    """Test failed password verification."""
    password = "SecurePass123!"
    wrong_password = "WrongPass456!"
    hashed = hash_password(password)
    
    assert verify_password(wrong_password, hashed) is False


def test_verify_password_invalid_hash():
    """Test password verification with invalid hash."""
    password = "SecurePass123!"
    invalid_hash = "not_a_valid_hash"
    
    assert verify_password(password, invalid_hash) is False


def test_generate_session_token():
    """Test session token generation."""
    token1 = generate_session_token()
    token2 = generate_session_token()
    
    # Should be non-empty
    assert len(token1) > 0
    
    # Should be different each time (cryptographically random)
    assert token1 != token2
    
    # Should be URL-safe (no special characters that need encoding)
    assert all(c.isalnum() or c in '-_' for c in token1)


def test_hash_token():
    """Test token hashing."""
    token = "test_session_token_123"
    hashed = hash_token(token)
    
    # Should be SHA-256 hex (64 characters)
    assert len(hashed) == 64
    assert all(c in '0123456789abcdef' for c in hashed)
    
    # Should be deterministic (same token = same hash)
    assert hash_token(token) == hashed
    
    # Different tokens should have different hashes
    assert hash_token("different_token") != hashed


def test_generate_csrf_token():
    """Test CSRF token generation."""
    session_id = "test-session-id-123"
    token = generate_csrf_token(session_id)
    
    # Should contain session ID and timestamp
    assert session_id in token
    
    # Should have 3 parts: session_id:timestamp:signature
    parts = token.split(':')
    assert len(parts) == 3
    
    # Timestamp should be valid integer
    assert parts[1].isdigit()


def test_verify_csrf_token_success():
    """Test successful CSRF token verification."""
    session_id = "test-session-id-123"
    token = generate_csrf_token(session_id)
    
    # Should verify successfully
    assert verify_csrf_token(token, session_id) is True


def test_verify_csrf_token_wrong_session():
    """Test CSRF token verification with wrong session ID."""
    session_id = "test-session-id-123"
    wrong_session_id = "different-session-id"
    token = generate_csrf_token(session_id)
    
    # Should fail verification
    assert verify_csrf_token(token, wrong_session_id) is False


def test_verify_csrf_token_expired():
    """Test CSRF token verification with expired token."""
    session_id = "test-session-id-123"
    token = generate_csrf_token(session_id)
    
    # Should fail verification if max age is 0 (immediate expiration)
    assert verify_csrf_token(token, session_id, max_age_seconds=0) is False


def test_verify_csrf_token_invalid_format():
    """Test CSRF token verification with invalid format."""
    session_id = "test-session-id-123"
    invalid_token = "invalid:token"
    
    # Should fail verification
    assert verify_csrf_token(invalid_token, session_id) is False


def test_verify_csrf_token_tampered():
    """Test CSRF token verification with tampered signature."""
    session_id = "test-session-id-123"
    token = generate_csrf_token(session_id)
    
    # Tamper with the signature
    parts = token.split(':')
    tampered_token = f"{parts[0]}:{parts[1]}:tampered_signature"
    
    # Should fail verification
    assert verify_csrf_token(tampered_token, session_id) is False


def test_check_rate_limit_under_limit():
    """Test rate limiting when under limit."""
    # Clear rate limit store
    _rate_limit_store.clear()
    
    ip = "192.168.1.1"
    endpoint = "test_endpoint"
    max_requests = 5
    
    # Should allow first 5 requests
    for i in range(max_requests):
        assert check_rate_limit(ip, endpoint, max_requests) is True


def test_check_rate_limit_exceed_limit():
    """Test rate limiting when exceeding limit."""
    # Clear rate limit store
    _rate_limit_store.clear()
    
    ip = "192.168.1.2"
    endpoint = "test_endpoint_2"
    max_requests = 3
    
    # First 3 requests should succeed
    for i in range(max_requests):
        assert check_rate_limit(ip, endpoint, max_requests) is True
    
    # 4th request should fail
    assert check_rate_limit(ip, endpoint, max_requests) is False


def test_check_rate_limit_window_expiration():
    """Test rate limiting window expiration."""
    # Clear rate limit store
    _rate_limit_store.clear()
    
    ip = "192.168.1.3"
    endpoint = "test_endpoint_3"
    max_requests = 2
    window_seconds = 1  # 1 second window
    
    # First 2 requests should succeed
    assert check_rate_limit(ip, endpoint, max_requests, window_seconds) is True
    assert check_rate_limit(ip, endpoint, max_requests, window_seconds) is True
    
    # 3rd request should fail
    assert check_rate_limit(ip, endpoint, max_requests, window_seconds) is False
    
    # Wait for window to expire
    time.sleep(1.1)
    
    # Should allow requests again
    assert check_rate_limit(ip, endpoint, max_requests, window_seconds) is True


def test_check_rate_limit_different_ips():
    """Test rate limiting is per-IP."""
    # Clear rate limit store
    _rate_limit_store.clear()
    
    ip1 = "192.168.1.4"
    ip2 = "192.168.1.5"
    endpoint = "test_endpoint_4"
    max_requests = 2
    
    # IP1 uses up its limit
    assert check_rate_limit(ip1, endpoint, max_requests) is True
    assert check_rate_limit(ip1, endpoint, max_requests) is True
    assert check_rate_limit(ip1, endpoint, max_requests) is False
    
    # IP2 should still have its full limit
    assert check_rate_limit(ip2, endpoint, max_requests) is True
    assert check_rate_limit(ip2, endpoint, max_requests) is True


def test_check_rate_limit_different_endpoints():
    """Test rate limiting is per-endpoint."""
    # Clear rate limit store
    _rate_limit_store.clear()
    
    ip = "192.168.1.6"
    endpoint1 = "test_endpoint_5"
    endpoint2 = "test_endpoint_6"
    max_requests = 2
    
    # Endpoint1 uses up its limit
    assert check_rate_limit(ip, endpoint1, max_requests) is True
    assert check_rate_limit(ip, endpoint1, max_requests) is True
    assert check_rate_limit(ip, endpoint1, max_requests) is False
    
    # Endpoint2 should still have its full limit
    assert check_rate_limit(ip, endpoint2, max_requests) is True
    assert check_rate_limit(ip, endpoint2, max_requests) is True
