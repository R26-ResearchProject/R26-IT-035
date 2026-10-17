"""Scoring logic for ranking candidate recommendations."""

from typing import Any, Dict, List


WEIGHTS = {
    "prakriti_match_score": 0.30,
    "condition_match_score": 0.25,
    "symptom_match_score": 0.20,
    "module_confidence_score": 0.10,
    "expert_weight": 0.10,
    "mapping_match_weight": 0.05,
}


def compute_candidate_score(
    user_input: Dict[str, Any],
    recommendation: Dict[str, Any],
    mapping: Dict[str, Any],
) -> Dict[str, Any]:
    """Compute weighted score plus transparent score components."""
    prakriti_result = user_input["prakriti_result"]
    skin_result = user_input["skin_result"]

    mapped_prakriti = mapping["prakriti"].lower()
    dominant_prakriti = str(prakriti_result["dominant_prakriti"]).lower()
    secondary_prakriti = str(prakriti_result["secondary_prakriti"]).lower()
    prakriti_scores = prakriti_result["prakriti_scores"]
    prakriti_match_score = _prakriti_match_score(
        mapped_prakriti=mapped_prakriti,
        dominant_prakriti=dominant_prakriti,
        secondary_prakriti=secondary_prakriti,
        prakriti_scores=prakriti_scores,
    )

    condition_match_score = (
        1.0 if mapping["condition"].lower() == skin_result["predicted_condition"].lower() else 0.0
    )

    user_symptoms = {symptom.lower() for symptom in skin_result["symptoms"]}
    mapped_symptoms = {symptom.lower() for symptom in mapping["symptoms"]}
    symptom_match_score = _symptom_overlap_score(user_symptoms, mapped_symptoms)

    module_confidence_score = (float(prakriti_result["confidence"]) + float(skin_result["confidence"])) / 2.0
    expert_weight = float(recommendation["expert_weight"])
    mapping_match_weight = float(mapping["match_weight"])

    score_components = {
        "prakriti_match_score": prakriti_match_score,
        "condition_match_score": condition_match_score,
        "symptom_match_score": symptom_match_score,
        "module_confidence_score": module_confidence_score,
        "expert_weight": expert_weight,
        "mapping_match_weight": mapping_match_weight,
    }

    final_score = sum(score_components[key] * WEIGHTS[key] for key in WEIGHTS)
    final_score = _apply_severity_penalty(final_score, skin_result["severity"], recommendation["advice_strength"])
    return {"final_score": round(final_score, 4), "score_components": score_components}


def _symptom_overlap_score(user_symptoms: set, mapped_symptoms: set) -> float:
    """Compute symptom signal using both coverage and overlap volume."""
    if not mapped_symptoms:
        return 0.0
    overlap = user_symptoms.intersection(mapped_symptoms)
    coverage = len(overlap) / len(mapped_symptoms)
    precision = len(overlap) / max(1, len(user_symptoms))
    return (coverage * 0.8) + (precision * 0.2)


def _prakriti_match_score(
    mapped_prakriti: str,
    dominant_prakriti: str,
    secondary_prakriti: str,
    prakriti_scores: Dict[str, float],
) -> float:
    """Score prakriti alignment for mixed profiles with secondary support."""
    base_score = float(prakriti_scores.get(mapped_prakriti, 0.0))
    if mapped_prakriti == dominant_prakriti:
        return min(1.0, base_score + 0.2)
    if mapped_prakriti == secondary_prakriti:
        return min(1.0, base_score + 0.1)
    return base_score


def _apply_severity_penalty(score: float, severity: str, advice_strength: str) -> float:
    """Penalize weak advice when skin severity is high."""
    sev = str(severity).lower()
    strength = str(advice_strength).lower()
    if sev == "mild":
        return score
    if sev == "moderate":
        if strength == "weak":
            return score * 0.82
        if strength == "moderate":
            return score * 0.92
        return score
    if sev == "severe":
        if strength == "weak":
            return score * 0.7
        if strength == "moderate":
            return score * 0.85
    return score


def rank_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort candidates by final score, highest first."""
    return sorted(candidates, key=lambda item: item["score"], reverse=True)
