"""Build explainable recommendation outputs and summaries."""

from typing import Any, Dict, List


def build_recommendation_reason(candidate: Dict[str, Any]) -> str:
    """Generate a short explanation sentence for one recommendation."""
    factors = candidate["matched_factors"]
    return (
        f"Selected because it aligns with {factors['prakriti']} traits, "
        f"{factors['condition']} support needs, and matched symptoms: "
        f"{', '.join(factors['symptoms']) if factors['symptoms'] else 'none'}."
    )


def build_confidence_explanation(user_input: Dict[str, Any], score_components: Dict[str, float]) -> str:
    """Explain confidence in plain language using module and symptom signals."""
    prakriti_conf = float(user_input["prakriti_result"]["confidence"])
    skin_conf = float(user_input["skin_result"]["confidence"])
    symptom_score = float(score_components["symptom_match_score"])
    return (
        f"Confidence combines prakriti ({prakriti_conf:.2f}) and skin condition ({skin_conf:.2f}) "
        f"signals, with symptom overlap score {symptom_score:.2f}."
    )


def build_summary(user_input: Dict[str, Any], count: int) -> str:
    """Create a recommendation summary for the response body."""
    dominant = user_input["prakriti_result"]["dominant_prakriti"]
    condition = user_input["skin_result"]["predicted_condition"]
    severity = user_input["skin_result"]["severity"]
    return (
        f"Generated {count} personalized recommendations using {dominant}-dominant prakriti "
        f"and {severity} {condition} profile."
    )


def build_explanation_summary(user_input: Dict[str, Any], recommendation_count: int) -> str:
    """Provide short explanation of why these recommendations were selected."""
    dominant = user_input["prakriti_result"]["dominant_prakriti"]
    secondary = user_input["prakriti_result"]["secondary_prakriti"]
    condition = user_input["skin_result"]["predicted_condition"]
    symptoms = ", ".join(user_input["skin_result"]["symptoms"][:3])
    return (
        f"Ranking prioritized {condition} mappings, mixed-prakriti alignment ({dominant}/{secondary}), "
        f"and symptom overlap ({symptoms if symptoms else 'no symptoms provided'}) across {recommendation_count} items."
    )


def default_safety_note() -> str:
    """Return baseline non-diagnostic disclaimer text."""
    return (
        "These recommendations are supportive lifestyle and home-care guidance only. "
        "They are not a substitute for professional medical diagnosis or treatment."
    )


def referral_only_payload(user_id: str, safety_messages: List[str]) -> Dict[str, Any]:
    """Create response payload when recommendation generation is blocked by safety gates."""
    note = " ".join(safety_messages) if safety_messages else default_safety_note()
    return {
        "user_id": user_id,
        "status": "referral_recommended",
        "recommendation_summary": "Personalized recommendations were deferred due to safety policy.",
        "overall_confidence_level": "low",
        "explanation_summary": "Safety-first policy prevented recommendation generation.",
        "recommendations_by_category": {"diet": [], "lifestyle": [], "home_care": []},
        "safety_note": note,
        "referral_warning": note,
    }
