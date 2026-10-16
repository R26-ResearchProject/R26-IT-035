# health.py
# Simple health check endpoint.
# Used to verify API is running.
# Test this first after starting server.

from fastapi import APIRouter

# Create router instance
router = APIRouter()


@router.get("/health")
def health_check():
    """
    Returns running status of the API.
    Visit http://localhost:8000/api/health
    to verify server is working.
    """
    return {
        "status": "running",
        "module": "Novelty 3 - Explanation Module",
        "version": "1.0.0"
    }
