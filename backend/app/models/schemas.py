# schemas.py
# PURPOSE: Defines the shape of data going in
# and out of the API endpoints.
# Pydantic automatically validates all inputs.

from pydantic import BaseModel, Field
from typing import Optional, List


class PrakritiInput(BaseModel):
    """
    Simple Prakriti input for direct testing.
    Used by /api/explanation/western endpoint.
    """
    vata: float = Field(
        ..., ge=0.0, le=1.0,
        description="Vata score 0 to 1"
    )
    pitta: float = Field(
        ..., ge=0.0, le=1.0,
        description="Pitta score 0 to 1"
    )
    kapha: float = Field(
        ..., ge=0.0, le=1.0,
        description="Kapha score 0 to 1"
    )


class ExplanationRequest(BaseModel):
    """
    Simple request for testing.
    Used by POST /api/explanation/western
    """
    disease_id: str = Field(
        ...,
        description="Disease ID from Novelty 2",
        example="eczema"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confidence from Novelty 2",
        example=0.94
    )
    prakriti: PrakritiInput


class PrakritiResult(BaseModel):
    """
    Prakriti output from Novelty 1.
    Contains body type scores and dominant type.
    """
    dominant_prakriti: str
    secondary_prakriti: Optional[str] = None
    prakriti_scores: dict  # {vata: 0.3, pitta: 0.6, kapha: 0.1}
    confidence: Optional[float] = None


class SkinResult(BaseModel):
    """
    Skin disease output from Novelty 2.
    Contains predicted disease and confidence.
    """
    predicted_condition: str
    confidence: float
    severity: Optional[str] = None
    symptoms: Optional[List[str]] = []
    referral_required: Optional[bool] = False


class UserContext(BaseModel):
    """
    Additional user information.
    Used to personalize explanation further
    beyond Prakriti-based personalization.
    """
    # adult, child, teenager, elderly
    age_group: Optional[str] = "adult"

    # True if user is pregnant
    # Triggers pregnancy safety modifications
    pregnancy_status: Optional[bool] = False

    # List of known allergens
    # Matched against disease triggers
    known_allergies: Optional[List[str]] = []

    preferred_language: Optional[str] = "English"


class CombinedInputRequest(BaseModel):
    """
    Combined input from Novelty 1 and Novelty 2.
    This is what the frontend sends to Novelty 3.
    Includes all information needed for full
    personalized dual explanation.
    """
    user_id: Optional[str] = None
    prakriti_result: PrakritiResult
    skin_result: SkinResult
    user_context: Optional[UserContext] = None