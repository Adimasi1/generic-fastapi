"""
schemas/user.py - Pydantic Schemas for User Data
=================================================

WHAT ARE SCHEMAS (vs MODELS)?
-----------------------------
- MODELS (SQLAlchemy): Define database tables, talk to PostgreSQL
- SCHEMAS (Pydantic): Define API data shapes, validate input/output

WHY SEPARATE THEM?
------------------
1. Different fields: DB has hashed_password, API never exposes it
2. Different validation: API validates input, DB enforces constraints
3. Flexibility: Can change API without changing DB, and vice versa

PYDANTIC V2 FEATURES USED:
--------------------------
- SecretStr: Hides password in logs and __repr__
- EmailStr: Validates email format automatically
- field_validator: Custom validation logic
- model_config: Configure serialization behavior
"""

from datetime import datetime
from uuid import UUID
import re

from pydantic import BaseModel, EmailStr, SecretStr, field_validator


# =============================================================================
# INPUT SCHEMAS (what the API receives)
# =============================================================================

class UserCreate(BaseModel):
    """
    Schema for user registration requests.
    
    Used at: POST /auth/register
    
    Example request body:
        {
            "email": "user@example.com",
            "password": "MySecure123"
        }
    """
    email: EmailStr  # Pydantic validates email format automatically
    password: SecretStr  # Hidden in logs, accessed via .get_secret_value()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: SecretStr) -> SecretStr:
        """
        Validate password strength requirements.
        
        Requirements:
            - At least 8 characters
            - At least one number (0-9)
            - At least one uppercase letter (A-Z)
        
        Note: @classmethod is required by Pydantic v2 for validators
        """
        pw = v.get_secret_value()  # Get the actual string from SecretStr
        
        if len(pw) < 8:
            raise ValueError("The password must be at least 8 characters long")
        if not re.search(r"[0-9]", pw):
            raise ValueError("The password must include at least a number")
        if not re.search(r"[A-Z]", pw):
            raise ValueError("The password must include at least a capital letter")
        
        return v


# =============================================================================
# OUTPUT SCHEMAS (what the API returns)
# =============================================================================

class UserRead(BaseModel):
    """
    Schema for user data in API responses.
    
    Used at: GET /users/me, registration response
    
    Note: Never includes password! Only safe fields.
    
    Example response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z"
        }
    """
    id: UUID
    email: EmailStr
    is_active: bool
    created_at: datetime

    # from_attributes=True allows creating this from SQLAlchemy model
    # UserRead.model_validate(db_user) works because of this
    model_config = {"from_attributes": True}


# =============================================================================
# TOKEN SCHEMAS (for JWT authentication)
# =============================================================================

class Token(BaseModel):
    """
    Schema for login response containing JWT token.
    
    Used at: POST /auth/login
    
    Example response:
        {
            "access_token": "eyJhbGciOiJSUzI1NiIs...",
            "token_type": "bearer"
        }
    """
    access_token: str
    token_type: str = "bearer"  # Always "bearer" for JWT


class TokenData(BaseModel):
    """
    Schema for decoded JWT token payload.
    
    Used internally to validate token data structure.
    Not returned to users - only used in auth.py
    """
    user_id: UUID | None = None  # Extracted from "sub" claim in JWT