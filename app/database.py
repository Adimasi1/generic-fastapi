"""
database.py - Database Connection and Session Management
=========================================================

This module sets up SQLAlchemy's connection to PostgreSQL.

KEY CONCEPTS:
-------------
1. ENGINE: The connection pool to the database
   - Manages multiple connections for concurrent requests
   - echo=True prints SQL queries to console (for debugging)

2. SESSIONLOCAL: Factory that creates database sessions
   - Each request gets its own session (isolation)
   - autocommit=False: We manually control transactions
   - autoflush=False: We decide when to sync with DB

3. BASE: Parent class for all ORM models
   - All models inherit from this (e.g., class User(Base))
   - Provides metadata for table creation

4. GET_DB: FastAPI dependency injection pattern
   - Yields a session to the endpoint
   - Automatically closes session after request completes
   - Even if an error occurs (finally block)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings


# =============================================================================
# DATABASE ENGINE
# =============================================================================
# Creates connection pool to PostgreSQL
# - settings.database_url: Connection string from config
# - echo: If True, prints all SQL queries (useful for debugging)
engine = create_engine(settings.database_url, echo=settings.debug)


# =============================================================================
# SESSION FACTORY
# =============================================================================
# Creates a class that produces new Session objects
# Each session = one unit of work with the database
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# =============================================================================
# DECLARATIVE BASE
# =============================================================================
# All ORM models inherit from this base class
Base = declarative_base()


# =============================================================================
# DEPENDENCY INJECTION FOR FASTAPI
# =============================================================================
def get_db():
    """
    Database session dependency for FastAPI endpoints.
    
    Usage in endpoints:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    
    How it works:
    1. FastAPI calls get_db() before the endpoint
    2. yield db - gives the session to the endpoint
    3. Endpoint uses db, then returns response
    4. finally: closes the session (even if endpoint raised error)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()