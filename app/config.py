"""
config.py - Centralized Application Configuration
===================================================

HOW IT WORKS IN PRODUCTION:
---------------------------
Pydantic-settings reads configuration in this priority order:
1. System environment variables (highest priority)
2. .env file (if it exists - for local development only)
3. Default values in the code (lowest priority)

In production, there is NO .env file - everything comes from environment variables
set by the deployment platform (AWS, Heroku, Docker, Kubernetes, etc.)

WHAT PYDANTIC-SETTINGS DOES AUTOMATICALLY:
- Reads environment variables
- Converts types (e.g., "1440" string -> 1440 int)
- Validates required fields exist
- Provides error messages if configuration is missing

EQUIVALENT MANUAL CODE (what Pydantic does under the hood):
    import os
    database_url = os.getenv("DATABASE_URL")
    if database_url is None:
        raise ValueError("DATABASE_URL not set!")
    access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
"""

from functools import lru_cache
import base64

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Each field maps to an environment variable:
        database_url        <- DATABASE_URL
        secret_key          <- SECRET_KEY
        private_key_base64  <- PRIVATE_KEY_BASE64
        public_key_base64   <- PUBLIC_KEY_BASE64
    
    Pydantic automatically converts UPPER_SNAKE_CASE to lower_snake_case.
    """
    
    # =========================================================================
    # DATABASE
    # =========================================================================
    database_url: str  # Required, no default - app won't start without it
    
    # =========================================================================
    # SECURITY
    # =========================================================================
    secret_key: str  # For other cryptographic operations (sessions, etc.)
    access_token_expire_minutes: int = 1440  # Default: 24 hours
    
    # =========================================================================
    # ENVIRONMENT
    # =========================================================================
    env: str = "development"  # development | staging | production
    debug: bool = False
    
    # =========================================================================
    # RSA KEYS FOR JWT (RS256)
    # =========================================================================
    # Keys are stored as base64 because:
    # - PEM files contain newlines (\n)
    # - Environment variables don't handle newlines well
    # - Base64 encodes everything into a single-line string
    private_key_base64: str = ""
    public_key_base64: str = ""
    
    @property
    def private_key(self) -> str:
        """
        Decode private key from base64 to PEM format.
        
        Used by auth.py to SIGN JWT tokens.
        This key must NEVER be shared or exposed!
        """
        if not self.private_key_base64:
            raise ValueError("PRIVATE_KEY_BASE64 not configured!")
        return base64.b64decode(self.private_key_base64).decode("utf-8")
    
    @property
    def public_key(self) -> str:
        """
        Decode public key from base64 to PEM format.
        
        Used by auth.py to VERIFY JWT tokens.
        This key can be shared publicly - it can only verify, not create tokens.
        """
        if not self.public_key_base64:
            raise ValueError("PUBLIC_KEY_BASE64 not configured!")
        return base64.b64decode(self.public_key_base64).decode("utf-8")

    # Pydantic-settings configuration
    model_config = {
        "env_file": ".env",           # Read from .env file if it exists
        "env_file_encoding": "utf-8",
        "extra": "ignore",            # Ignore extra env vars not defined here
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (singleton pattern with caching).
    
    @lru_cache() ensures Settings() is instantiated only ONCE.
    All subsequent calls return the same instance.
    
    Benefits:
        - Avoids re-reading .env or env vars on every request
        - Better performance
        - Consistency (same settings everywhere)
    """
    return Settings()


# Global instance for direct import: from app.config import settings
settings = get_settings()