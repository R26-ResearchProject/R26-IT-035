"""Schema and type helpers for recommendation engine inputs/outputs."""

from typing import Any, Dict, List, TypedDict


class PrakritiResult(TypedDict):
    dominant_prakriti: str
    secondary_prakriti: str
    prakriti_scores: Dict[str, float]
    confidence: float


class SkinResult(TypedDict):
    predicted_condition: str
    confidence: float
    severity: str
    symptoms: List[str]
    referral_required: bool


class UserContext(TypedDict):
    age_group: str
    known_allergies: List[str]
    pregnancy_status: bool
    preferred_language: str
    dietary_preference: str


class ModuleInput(TypedDict):
    user_id: str
    prakriti_result: PrakritiResult
    skin_result: SkinResult
    user_context: UserContext


JsonDict = Dict[str, Any]
