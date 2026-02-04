"""
FastAPI application entry point.

This module initializes the FastAPI app, configures middleware (CORS),
and registers routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_supabase_client
from app.routers import auth, packages, receipts, dashboard

# Initialize FastAPI application
app = FastAPI(
    title="Backend API",
    description="Production-ready FastAPI backend",
    version="1.0.0",
)


@app.on_event("startup")
async def startup():
    """Initialize Supabase client on startup."""
    init_supabase_client()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint to verify backend is running.

    Returns:
        dict: Status message
    """
    return {"status": "Backend running"}


# Register routers
app.include_router(auth.router)
app.include_router(packages.router)
app.include_router(receipts.router)
app.include_router(dashboard.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.env == "development",
    )
