"""Load and validate JSON files used by the recommendation engine."""

import json
from pathlib import Path
from typing import Any, Dict, List


REQUIRED_TOP_LEVEL_KEYS = ["user_id", "prakriti_result", "skin_result", "user_context"]
REQUIRED_PRAKRITI_KEYS = ["dominant_prakriti", "secondary_prakriti", "prakriti_scores", "confidence"]
REQUIRED_SKIN_KEYS = ["predicted_condition", "confidence", "severity", "symptoms", "referral_required"]
REQUIRED_CONTEXT_KEYS = ["age_group", "known_allergies", "pregnancy_status", "preferred_language"]


def load_json(path: Path) -> Any:
    """Read and parse a JSON file."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_input(payload: Dict[str, Any]) -> None:
    """Validate required module input fields."""
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in payload:
            raise ValueError(f"Missing required top-level field: {key}")

    _validate_section(payload["prakriti_result"], REQUIRED_PRAKRITI_KEYS, "prakriti_result")
    _validate_section(payload["skin_result"], REQUIRED_SKIN_KEYS, "skin_result")
    _validate_section(payload["user_context"], REQUIRED_CONTEXT_KEYS, "user_context")

    if not isinstance(payload["skin_result"]["symptoms"], list):
        raise ValueError("skin_result.symptoms must be a list")

    if not isinstance(payload["prakriti_result"]["prakriti_scores"], dict):
        raise ValueError("prakriti_result.prakriti_scores must be a dictionary")


def load_knowledge_base(data_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Load recommendation, mapping, and safety files from data folder."""
    recommendations = load_json(data_dir / "recommendations.json")
    mappings = load_json(data_dir / "mappings.json")
    safety_rules = load_json(data_dir / "safety_rules.json")
    return {
        "recommendations": recommendations,
        "mappings": mappings,
        "safety_rules": safety_rules,
    }


def _validate_section(section: Dict[str, Any], required_keys: List[str], section_name: str) -> None:
    """Check required keys in one section of the input payload."""
    for key in required_keys:
        if key not in section:
            raise ValueError(f"Missing required field in {section_name}: {key}")
