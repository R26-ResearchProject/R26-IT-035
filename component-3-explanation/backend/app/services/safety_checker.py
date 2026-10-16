# safety_checker.py
# Checks if a disease is dangerous before
# generating any explanation.
# This is the FIRST thing that runs when
# a disease name arrives from Novelty 2.

import json
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Load dangerous diseases list once when file loads
# This file is read from dangerous_diseases.json
try:
    with open("app/data/safety/dangerous_diseases.json") as f:
        DANGEROUS_DATA = json.load(f)
    logger.info("Dangerous diseases list loaded successfully")
except Exception as e:
    logger.error(f"Could not load dangerous diseases file: {e}")
    DANGEROUS_DATA = {}

# Keywords that always trigger safety block
# Even if disease name is not in the exact list
DANGEROUS_KEYWORDS = [
    "cancer", "carcinoma", "melanoma",
    "sarcoma", "lymphoma", "malignant",
    "necrotizing", "stevens_johnson",
    "toxic_epidermal"
]

# Messages shown to user for each danger level
SAFETY_MESSAGES = {

    "critical": {
        "level": "critical",
        "title": "Immediate Medical Attention Required",
        "message": (
            "Our system has identified a potentially serious "
            "skin condition that requires immediate evaluation "
            "by a qualified medical professional. This condition "
            "cannot be assessed or managed through an AI application."
        ),
        "action": (
            "Please visit a dermatologist, oncologist, or "
            "emergency medical facility as soon as possible. "
            "Do not delay seeking professional medical care."
        ),
        "show_explanation": False,
        "show_ayurveda": False,
        "emergency_contacts": True
    },

    "urgent": {
        "level": "urgent",
        "title": "Urgent Medical Evaluation Needed",
        "message": (
            "The identified condition requires prompt evaluation "
            "by a medical professional. This is not a condition "
            "suitable for self-management without medical supervision."
        ),
        "action": (
            "Please consult a dermatologist within 24 to 48 hours. "
            "If symptoms are worsening rapidly, seek emergency care."
        ),
        "show_explanation": False,
        "show_ayurveda": False,
        "emergency_contacts": False
    },

    "supervision": {
        "level": "supervision",
        "title": "Medical Supervision Required",
        "message": (
            "The identified condition is complex and requires "
            "ongoing supervision by a qualified physician. "
            "Management should only be done under medical guidance."
        ),
        "action": (
            "Please consult a dermatologist or specialist. "
            "Ayurvedic practices may complement but should never "
            "replace prescribed medical treatment."
        ),
        "show_explanation": False,
        "show_ayurveda": False,
        "emergency_contacts": False
    }
}


def check_disease_safety(disease_id: str):
    """
    Checks if a disease requires medical referral.

    How it works:
    1. Checks exact match against dangerous disease lists
    2. Checks keyword match for variants
       (e.g. 'skin_cancer' contains 'cancer')

    Returns:
    - None if disease is safe to explain
    - Safety response dict if disease is dangerous
    """

    disease_lower = disease_id.lower()

    # Check each danger level list
    for level_key, level_data in DANGEROUS_DATA.items():

        diseases_in_level = level_data.get("diseases", [])
        message_type = level_data.get("message_type", "critical")

        # Check exact match
        if disease_lower in diseases_in_level:
            logger.warning(
                f"Safety block triggered for: {disease_id} "
                f"(level: {message_type})"
            )
            return SAFETY_MESSAGES[message_type]

    # Check keyword match
    # This catches variants like 'basal_cell_cancer'
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in disease_lower:
            logger.warning(
                f"Safety keyword '{keyword}' found in: {disease_id}"
            )
            return SAFETY_MESSAGES["critical"]

    # Disease is safe — return None to continue
    logger.info(f"Safety check passed for: {disease_id}")
    return None