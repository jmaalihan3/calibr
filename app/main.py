"""
FastAPI application entry point.

This module:
- Initializes the FastAPI app
- Configures CORS for development
- Includes API routers
- Serves frontend static files
- Initializes database on startup

Development: Run with `uvicorn app.main:app --reload --port 8000`
Production: Would need proper CORS config, HTTPS, etc.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from app.routers import exams, auth
from app import db
from app.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    
    Startup:
        - Initialize database schema
        - Populate sample questions if needed
    
    Shutdown:
        - No cleanup needed (SQLite auto-manages connections)
    """
    # Startup: Initialize database
    db.init_db()
    print("Database initialized")
    
    yield
    
    # Shutdown: No cleanup needed
    print("Application shutdown")


# Initialize FastAPI app
app = FastAPI(
    title="Academic Assessment API",
    description="REST API for exam generation and submission",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
# Production: Only allow the deployed URL
# Development: Allow localhost for testing
if config.is_production():
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        allowed_origins = [
            render_url,
            render_url.replace("http://", "https://")
        ]
    else:
        allowed_origins = []
else:
    allowed_origins = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (must be before static files mount)
@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        {"status": "ok"}
    
    Use: Verify API is running
    """
    return {"status": "ok", "message": "API is running"}


# Include API routers
app.include_router(auth.router)
app.include_router(exams.router)


# Mount frontend static files
# This serves index.html at GET / and other static assets
# Placed last so API routes take precedence
try:
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
except RuntimeError:
    # Directory doesn't exist yet - will be created later
    print("Warning: frontend/ directory not found. Create it to serve static files.")
