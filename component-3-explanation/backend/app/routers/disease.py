# disease.py
# API endpoints for disease information.
# Used to list and retrieve disease data
# from the knowledge base dataset.

from fastapi import APIRouter, HTTPException
from app.services.mongodb_client import get_database
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create router instance
router = APIRouter()


@router.get("/diseases")
def get_all_diseases():
    """
    Returns list of all 20 diseases in the dataset.
    Shows only id and name — not full data.

    Test: GET http://localhost:8000/api/diseases
    """
    try:
        db = get_database()

        # Get all diseases, return only id and name
        diseases = list(
            db.diseases.find(
                {},
                # Include only these fields
                {"disease_id": 1, "name": 1, "_id": 0}
            )
        )

        return {
            "total": len(diseases),
            "diseases": diseases
        }

    except Exception as e:
        logger.error(f"Error fetching diseases: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not fetch diseases"
        )


@router.get("/diseases/{disease_id}")
def get_disease_by_id(disease_id: str):
    """
    Returns full data for one specific disease.

    Test: GET http://localhost:8000/api/diseases/eczema
    """
    try:
        db = get_database()

        # Find disease by ID
        disease = db.diseases.find_one(
            {"disease_id": disease_id},
            {"_id": 0}  # Exclude MongoDB internal ID
        )

        # Return 404 if not found
        if not disease:
            raise HTTPException(
                status_code=404,
                detail=f"Disease '{disease_id}' not found"
            )

        return disease

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching disease {disease_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not fetch disease"
        )