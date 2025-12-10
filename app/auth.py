"""
auth.py - JWT Authentication with RS256
========================================

This module handles JWT token creation and verification using RSA asymmetric encryption.

AUTHENTICATION FLOW:
1. User sends email/password to POST /auth/login
2. Server verifies password using bcrypt
3. Server creates JWT signed with PRIVATE KEY (only server has it)
4. Client receives token and includes it in subsequent requests
5. Server verifies token with PUBLIC KEY

WHY RS256 (RSA + SHA-256)?
- Asymmetric: private key signs, public key verifies
- Even if someone gets the public key, they CANNOT create fake tokens
- Only the private key holder (our server) can sign tokens
- Better security for public APIs with external clients
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import settings


# =============================================================================
# CONSTANTS
# =============================================================================

# JWT signing algorithm: RSA Signature with SHA-256
ALGORITHM = "RS256"


# =============================================================================
# OAUTH2 CONFIGURATION
# =============================================================================

# OAuth2PasswordBearer tells FastAPI:
# - Look for token in "Authorization: Bearer <token>" header
# - tokenUrl is used for Swagger UI documentation (login button)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# =============================================================================
# TOKEN CREATION
# =============================================================================

def create_access_token(
    user_id: UUID,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT token signed with the RSA private key.
    
    Args:
        user_id: The user's UUID (will be stored in "sub" claim)
        expires_delta: Custom token duration. If None, uses settings default.
    
    Returns:
        JWT token string like "eyJhbGciOiJSUzI1NiI..."
    
    JWT Payload structure:
        {
            "sub": "550e8400-e29b-41d4-a716-446655440000",  # Subject: who
            "exp": 1702000000,  # Expiration: Unix timestamp
            "iat": 1701913600   # Issued At: when created
        }
    """
    # Calculate expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    # Build JWT payload with standard claims
    payload = {
        "sub": str(user_id),                # Subject: identifies the user
        "exp": expire,                      # Expiration: when token becomes invalid
        "iat": datetime.now(timezone.utc)   # Issued At: creation timestamp
    }
    
    # Sign with private key
    token = jwt.encode(payload, settings.private_key, algorithm=ALGORITHM)
    
    return token


# =============================================================================
# TOKEN VERIFICATION
# =============================================================================

def verify_token(token: str) -> dict:
    """
    Verify a JWT token using the RSA public key.
    
    Args:
        token: The JWT token string to verify
    
    Returns:
        The decoded payload dict if token is valid
    
    Raises:
        HTTPException 401: If token is invalid, expired, or tampered with
    
    Verification process (inside jwt.decode):
        1. Split token into header.payload.signature
        2. Verify signature using public key
        3. Check that "exp" claim hasn't passed
        4. Return decoded payload if all checks pass
    """
    # Prepare exception to raise on any authentication failure
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode and verify token with public key
        # - Checks signature validity
        # - Checks expiration automatically
        payload = jwt.decode(
            token,
            settings.public_key,
            algorithms=[ALGORITHM]  # Note: 'algorithms' is a list
        )
        
        # Ensure "sub" claim exists
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        return payload
        
    except jwt.PyJWTError:
        # Catches: ExpiredSignatureError, InvalidSignatureError, DecodeError, etc.
        raise credentials_exception


# =============================================================================
# FASTAPI DEPENDENCY
# =============================================================================

async def get_current_user_id(
    token: str = Depends(oauth2_scheme)
) -> UUID:
    """
    FastAPI dependency to extract and verify user ID from JWT token.
    
    Usage in endpoints:
        @router.get("/my-credits")
        async def get_credits(user_id: UUID = Depends(get_current_user_id)):
            # user_id is already extracted and verified!
            ...
    
    How it works:
        1. FastAPI sees Depends(oauth2_scheme)
        2. oauth2_scheme extracts token from "Authorization: Bearer <token>"
        3. Token is passed to this function
        4. We verify and extract user_id
        5. If anything fails, FastAPI returns 401 automatically
    
    Args:
        token: JWT token (automatically extracted from Authorization header)
    
    Returns:
        The user's UUID extracted from the token
    """
    payload = verify_token(token)
    user_id = UUID(payload["sub"])
    return user_id
