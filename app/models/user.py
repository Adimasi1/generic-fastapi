"""
models/user.py - User Database Model (ORM)
===========================================

This defines the User table structure in the database.

WHAT IS AN ORM MODEL?
---------------------
ORM (Object-Relational Mapping) lets you work with database tables
as Python classes. Instead of writing SQL:
    INSERT INTO users (email, hashed_password) VALUES ('a@b.com', 'xyz')

You write Python:
    user = User(email='a@b.com', hashed_password='xyz')
    db.add(user)
    db.commit()

SQLALCHEMY 2.0 STYLE:
---------------------
We use the new Mapped[] and mapped_column() syntax:
    id: Mapped[uuid.UUID] = mapped_column(...)

This provides better type hints and IDE support than the old style:
    id = Column(UUID, ...)  # Old SQLAlchemy 1.x style

COLUMN OPTIONS:
---------------
- primary_key=True: This is the unique identifier
- unique=True: No two rows can have the same value
- nullable=False: This field is required (NOT NULL in SQL)
- index=True: Creates a database index for faster queries
- default=...: Default value if not provided
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, Uuid
from sqlalchemy.orm import mapped_column, Mapped

from app.database import Base


class User(Base):
    """
    User model representing the 'users' table in the database.
    
    Columns:
        id: UUID primary key (auto-generated)
        email: Unique email address (used for login)
        hashed_password: bcrypt-hashed password (NEVER store plain text!)
        is_active: Whether the user can log in
        created_at: Timestamp of account creation
    """
    __tablename__ = "users"
    
    # Primary key - UUID is better than auto-increment int for distributed systems
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, 
        primary_key=True, 
        default=uuid.uuid4  # Auto-generate UUID for new users
    )
    
    # Email - indexed for fast lookup during login
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True,     # No duplicate emails
        nullable=False,  # Required field
        index=True       # Fast lookup: SELECT * FROM users WHERE email = ...
    )
    
    # Password hash - NEVER store plain text passwords!
    # This stores the bcrypt hash from passlib
    hashed_password: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    # Account status - can be used to deactivate accounts without deleting
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True  # New accounts are active by default
    )
    
    # Audit timestamp - timezone-aware UTC datetime
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc)  # Always use UTC!
    )