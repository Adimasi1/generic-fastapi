"""
services/user_service.py - User Business Logic
===============================================

WHAT IS A SERVICE LAYER?
------------------------
Services contain the business logic of your application.
They sit between the API layer (routers) and the data layer (models).

    [Router] -> [Service] -> [Model/DB]
    
    Router: HTTP request/response handling
    Service: Business rules, validation, orchestration
    Model: Database operations

WHY SEPARATE SERVICES?
----------------------
1. Reusability: Same logic can be used by different endpoints
2. Testability: Easy to test business logic in isolation
3. Clean code: Routers stay thin, logic is organized

PASSWORD HASHING:
-----------------
We use passlib with bcrypt:
- bcrypt is slow BY DESIGN (prevents brute force attacks)
- Salt is automatically generated and included in hash
- Example hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.5T/V4vN4pHve

NEVER store plain text passwords!
"""

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate


# =============================================================================
# PASSWORD HASHING CONFIGURATION
# =============================================================================
# CryptContext handles password hashing and verification
# schemes=["bcrypt"]: Use bcrypt algorithm
# deprecated="auto": Automatically upgrade old hash formats
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =============================================================================
# USER OPERATIONS
# =============================================================================

def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Create a new user in the database.
    
    Args:
        db: SQLAlchemy database session
        user_in: Validated user data from request (email + password)
    
    Returns:
        User: The newly created user object
    
    Process:
        1. Extract plain password from SecretStr
        2. Hash the password with bcrypt
        3. Create User model with hashed password
        4. Save to database
        5. Return the created user
    
    Example:
        user_data = UserCreate(email="a@b.com", password="Secret123")
        new_user = create_user(db, user_data)
        # new_user.id is now a UUID
    """
    # Step 1: Extract password from SecretStr wrapper
    # SecretStr.get_secret_value() returns the actual string
    plain_password = user_in.password.get_secret_value()
    
    # Step 2: Hash password with bcrypt
    # This creates a unique salt and combines it with the hash
    hashed_password = pwd_context.hash(plain_password)
    
    # Step 3: Create User model (NOT schema - this is the DB object)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=True
    )
    
    # Step 4: Database operations
    db.add(db_user)      # Add to session (not yet in DB)
    db.commit()          # Write to database
    db.refresh(db_user)  # Reload from DB to get generated values (id, created_at)
    
    # Step 5: Return the created user
    return db_user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a bcrypt hash.
    
    Args:
        plain_password: The password provided by the user
        hashed_password: The stored hash from the database
    
    Returns:
        bool: True if password matches, False otherwise
    
    Used by: Login endpoint to verify credentials
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Find a user by their email address.
    
    Args:
        db: SQLAlchemy database session
        email: Email address to search for
    
    Returns:
        User if found, None otherwise
    
    Used by: Login endpoint to find user, registration to check duplicates
    """
    return db.query(User).filter(User.email == email).first()