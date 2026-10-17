"""Safety checks and filtering for recommendations."""

from typing import Any, Dict, List, Tuple


def evaluate_global_safety(user_input: Dict[str, Any], safety_rules: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate early safety gates before recommendation ranking."""
    skin_result = user_input["skin_result"]
    prakriti_result = user_input["prakriti_result"]
    checks = {
        "allow_recommendations": True,
        "personalization_factor": 1.0,
        "safety_messages": [],
    }

    if bool(skin_result["referral_required"]):
        checks["allow_recommendations"] = False
        checks["safety_messages"].append("Referral is required. Please consult a dermatologist first.")
        return checks

    if (
        bool(safety_rules.get("severe_conditions_require_referral", True))
        and str(skin_result["severity"]).lower() == "severe"
    ):
        checks["allow_recommendations"] = False
        checks["safety_messages"].append("Severe condition detected. Professional consultation is recommended first.")
        return checks

    if float(skin_result["confidence"]) < float(safety_rules["minimum_skin_confidence"]):
        checks["allow_recommendations"] = False
        checks["safety_messages"].append("Skin-condition confidence is low. Please verify with a clinician.")
        return checks

    if float(prakriti_result["confidence"]) < float(safety_rules["minimum_prakriti_confidence"]):
        checks["personalization_factor"] = 0.85
        checks["safety_messages"].append(
            "Prakriti confidence is low; personalization strength has been reduced."
        )

    return checks


def apply_recommendation_safety_filters(
    candidates: List[Dict[str, Any]],
    user_input: Dict[str, Any],
    safety_rules: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], List[str], List[Dict[str, Any]]]:
    """Remove blocked/risky/diet-conflicting recommendations and collect caution notes.

    Returns (safe_candidates, caution_messages, exclusions) where exclusions carries
    a structured {rec_id, title, rule, reason} entry per dropped candidate so the
    follow-up Q&A layer can explain "why not X" accurately instead of guessing.
    """
    context = user_input["user_context"]
    blocked_tags: List[str] = []
    blocked_map = safety_rules.get("blocked_recommendation_tags", {})

    if bool(context.get("pregnancy_status", False)):
        blocked_tags.extend(blocked_map.get("pregnancy", []))
    if str(context.get("age_group", "")).lower() == "child":
        blocked_tags.extend(blocked_map.get("child", []))

    known_allergies = {str(item).lower() for item in context.get("known_allergies", [])}

    dietary_preference = str(context.get("dietary_preference", "")).lower()
    dietary_exclusion_map = safety_rules.get("dietary_exclusions", {})
    dietary_excluded_tags = {tag.lower() for tag in dietary_exclusion_map.get(dietary_preference, [])}

    safe_candidates: List[Dict[str, Any]] = []
    cautions: List[str] = []
    exclusions: List[Dict[str, Any]] = []

    for candidate in candidates:
        tags = {tag.lower() for tag in candidate["tags"]}
        dietary_tags = {tag.lower() for tag in candidate.get("dietary_tags", [])}

        if any(blocked_tag.lower() in tags for blocked_tag in blocked_tags):
            exclusions.append(
                _exclusion(candidate, "context_block", "Blocked for the current pregnancy/age-group context.")
            )
            continue

        if known_allergies and tags.intersection(known_allergies):
            reason = f"Overlaps with known allergy tags: {', '.join(sorted(tags.intersection(known_allergies)))}."
            cautions.append(f"Recommendation {candidate['rec_id']} may overlap with known allergy tags; excluded for safety.")
            exclusions.append(_exclusion(candidate, "allergy", reason))
            continue

        if dietary_excluded_tags and dietary_tags.intersection(dietary_excluded_tags):
            conflict = ", ".join(sorted(dietary_tags.intersection(dietary_excluded_tags)))
            reason = f"Conflicts with '{dietary_preference}' dietary preference (tags: {conflict})."
            cautions.append(f"Recommendation {candidate['rec_id']} excluded due to dietary preference conflict.")
            exclusions.append(_exclusion(candidate, "dietary_preference", reason))
            continue

        if candidate.get("safety_level") == "risky":
            cautions.append(f"Recommendation {candidate['rec_id']} marked risky; excluded.")
            exclusions.append(_exclusion(candidate, "risky", "Marked as a risky recommendation."))
            continue

        safe_candidates.append(candidate)

    return safe_candidates, cautions, exclusions


def _exclusion(candidate: Dict[str, Any], rule: str, reason: str) -> Dict[str, Any]:
    """Build a structured exclusion record for follow-up explanations."""
    return {
        "rec_id": candidate["rec_id"],
        "title": candidate.get("title", ""),
        "rule": rule,
        "reason": reason,
    }
