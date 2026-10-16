# explanation.py
# PURPOSE: API endpoints for explanation generation.
#
# TWO ENDPOINTS:
# 1. POST /api/explanation/western
#    Simple format for testing
#    disease_id + confidence + prakriti
#
# 2. POST /api/explanation/full
#    Full format for real integration
#    Accepts combined Novelty 1 + 2 output
#    Includes user_context for personalization

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    ExplanationRequest,
    CombinedInputRequest
)
from app.services.explanation_generator import (
    generate_explanation
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post("/explanation/western")
def get_western_explanation(request: ExplanationRequest):
    """
    Simple endpoint for testing.

    Accepts basic format:
    {
        "disease_id": "eczema",
        "confidence": 0.94,
        "prakriti": {
            "vata": 0.30,
            "pitta": 0.60,
            "kapha": 0.10
        }
    }

    No user_context — for quick testing only.
    """
    try:
        logger.info(
            f"Simple request: {request.disease_id}"
        )

        # Convert pydantic model to dict
        prakriti_dict = {
            "vata": request.prakriti.vata,
            "pitta": request.prakriti.pitta,
            "kapha": request.prakriti.kapha
        }

        # Generate without user context
        result = generate_explanation(
            disease_id=request.disease_id,
            confidence=request.confidence,
            prakriti=prakriti_dict,
            user_context=None
        )

        return result

    except Exception as e:
        logger.error(f"Simple explanation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/explanation/full")
def get_full_explanation(request: CombinedInputRequest):
    """
    Full endpoint for real integration.

    Accepts combined Novelty 1 + 2 output:
    {
        "user_id": "U001",
        "prakriti_result": {
            "dominant_prakriti": "Pitta",
            "prakriti_scores": {
                "vata": 0.30,
                "pitta": 0.60,
                "kapha": 0.10
            },
            "confidence": 0.81
        },
        "skin_result": {
            "predicted_condition": "Eczema",
            "confidence": 0.87,
            "referral_required": false
        },
        "user_context": {
            "age_group": "adult",
            "pregnancy_status": false,
            "known_allergies": []
        }
    }
    """
    try:
        logger.info(
            f"Full request: "
            f"{request.skin_result.predicted_condition}"
        )

        # Extract disease from Novelty 2 output
        # Convert to lowercase with underscores
        disease_id = (
            request.skin_result.predicted_condition
            .lower()
            .replace(" ", "_")
        )
        confidence = request.skin_result.confidence

        # Extract Prakriti from Novelty 1 output
        prakriti_dict = (
            request.prakriti_result.prakriti_scores
        )

        # Check if Novelty 2 already flagged referral
        # If so, return safety referral immediately
        if request.skin_result.referral_required:
            return {
                "type": "safety_referral",
                "disease_id": disease_id,
                "safety": {
                    "level": "urgent",
                    "title": "Medical Referral Required",
                    "message": (
                        "Novelty 2 has flagged this "
                        "condition as requiring medical "
                        "referral. Please consult a "
                        "dermatologist."
                    ),
                    "action": (
                        "Please consult a dermatologist "
                        "as soon as possible."
                    ),
                    "show_explanation": False,
                    "show_ayurveda": False,
                    "emergency_contacts": False
                }
            }

        # Extract user context for personalization
        # pregnancy, age, allergies
        user_context = None
        if request.user_context:
            user_context = {
                "age_group": (
                    request.user_context.age_group
                    or "adult"
                ),
                "pregnancy_status": (
                    request.user_context.pregnancy_status
                    or False
                ),
                "known_allergies": (
                    request.user_context.known_allergies
                    or []
                )
            }

        # Generate complete explanation with context
        result = generate_explanation(
            disease_id=disease_id,
            confidence=confidence,
            prakriti=prakriti_dict,
            user_context=user_context
        )

        return result

    except Exception as e:
        logger.error(f"Full explanation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )