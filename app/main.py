"""
main.py - FastAPI Application Entry Point
==========================================

This is where the FastAPI application is instantiated and configured.

WHAT HAPPENS HERE:
------------------
1. Create the FastAPI app instance
2. Include all routers (auth, convert, credits, etc.)
3. Define global routes (health check)
4. Configure middleware, CORS, exception handlers

HOW TO RUN:
-----------
Development:
    uvicorn app.main:app --reload

Production:
    gunicorn app.main:app -k uvicorn.workers.UvicornWorker
"""

from fastapi import FastAPI
from app.routers.auth import router as auth_router

# =============================================================================
# APPLICATION INSTANCE
# =============================================================================
app = FastAPI(
    title="API Converter Service",
    description="SaaS API for data format conversion with credits system",
    version="0.1.0",
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# =============================================================================
# ROUTERS
# =============================================================================
# TODO: Include routers as they are created
# app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# app.include_router(convert_router, prefix="/convert", tags=["Conversion"])
# app.include_router(credits_router, prefix="/credits", tags=["Credits"])


# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================
@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns 200 OK if the application is running.
    Used by:
    - Kubernetes liveness probes
    - AWS ALB health checks
    - Monitoring systems (Datadog, Prometheus, etc.)
    """
    return {"status": "healthy"}

