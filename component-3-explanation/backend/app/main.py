# main.py
# FastAPI application entry point.
# This file starts the entire backend server.
# Run with: uvicorn app.main:app --reload --port 8000

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import explanation, disease, health
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=(
        "Novelty 3 — Explainable dual-perspective "
        "skin disease explanation module combining "
        "Western dermatology and Ayurvedic medicine"
    ),
    version="1.0.0"
)

# Add CORS middleware
# This allows React frontend to call this API
# Without this, browser will block the requests
app.add_middleware(
    CORSMiddleware,
    # Allow requests from React dev server
    allow_origins=[
        "http://localhost:5175",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://localhost:9000",
        "http://127.0.0.1:9000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register all routers with /api prefix
# health router:      /api/health
# disease router:     /api/diseases
# explanation router: /api/explanation/western
app.include_router(
    health.router,
    prefix="/api",
    tags=["Health"]
)
app.include_router(
    disease.router,
    prefix="/api",
    tags=["Diseases"]
)
app.include_router(
    explanation.router,
    prefix="/api",
    tags=["Explanation"]
)


@app.get("/")
def root():
    """
    Root endpoint. Visit http://localhost:8000
    to confirm server is running.
    """
    return {
        "message": "Novelty 3 API is running",
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/api/health"
    }


@app.on_event("startup")
async def startup_event():
    """
    Runs when server starts.
    Logs confirmation message.
    """
    logger.info("Novelty 3 API started successfully")
    logger.info(
        f"API docs available at: http://localhost:8000/docs"
    )