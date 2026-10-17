# fuzzy_engine.py
# The core reasoning engine of Novelty 3.
# Takes disease dosha values from dataset
# and user Prakriti scores from Novelty 1.
# Computes how strongly the disease affects
# this specific user using fuzzy logic.

from app.services.mongodb_client import get_database
from app.utils.logger import get_logger

logger = get_logger(__name__)


def compute_emphasis(disease_data: dict, user_prakriti: dict) -> dict:
    """
    Computes dosha emphasis weights for a specific user.

    How it works:
    1. Gets disease dosha aggravation values from dataset
       Example: eczema = {pitta: 0.80, vata: 0.30, kapha: 0.50}

    2. Gets user Prakriti scores from Novelty 1
       Example: {pitta: 0.60, vata: 0.30, kapha: 0.10}

    3. Multiplies them together (fuzzy intersection)
       pitta: 0.80 x 0.60 = 0.48
       vata:  0.30 x 0.30 = 0.09
       kapha: 0.50 x 0.10 = 0.05

    4. Normalizes so they add up to 100%
       pitta: 0.48 / 0.62 = 0.774 (77.4%)
       vata:  0.09 / 0.62 = 0.145 (14.5%)
       kapha: 0.05 / 0.62 = 0.081 (8.1%)

    Returns:
    Dictionary of emphasis weights per dosha
    Example: {pitta: 0.774, vata: 0.145, kapha: 0.081}
    """

    try:
        # Get disease dosha aggravation from dataset
        disease_dosha = disease_data.get("dosha_aggravation", {})

        # Validate all three doshas exist
        for dosha in ["vata", "pitta", "kapha"]:
            if dosha not in disease_dosha:
                disease_dosha[dosha] = 0.33
            if dosha not in user_prakriti:
                user_prakriti[dosha] = 0.33

        # Step 1: Fuzzy multiplication
        # Higher disease aggravation + higher user Prakriti
        # = stronger effect on this user
        raw_scores = {}
        for dosha in ["vata", "pitta", "kapha"]:
            raw_scores[dosha] = (
                disease_dosha[dosha] * user_prakriti[dosha]
            )

        logger.info(f"Raw fuzzy scores: {raw_scores}")

        # Step 2: Normalize to percentages
        total = sum(raw_scores.values())

        # Avoid division by zero
        if total == 0:
            return {"vata": 0.33, "pitta": 0.33, "kapha": 0.33}

        emphasis = {}
        for dosha in ["vata", "pitta", "kapha"]:
            # Round to 3 decimal places
            emphasis[dosha] = round(raw_scores[dosha] / total, 3)

        logger.info(
            f"Fuzzy emphasis computed: {emphasis} "
            f"for disease: {disease_data.get('disease_id')}"
        )

        return emphasis

    except Exception as e:
        logger.error(f"Fuzzy engine error: {e}")
        # Return equal distribution as fallback
        return {"vata": 0.33, "pitta": 0.33, "kapha": 0.33}


def get_dominant_dosha(emphasis: dict) -> str:
    """
    Returns the dosha with highest emphasis score.
    This is used to select personalized advice.

    Example:
    emphasis = {pitta: 0.774, vata: 0.145, kapha: 0.081}
    returns: "pitta"
    """
    return max(emphasis, key=emphasis.get)


def get_secondary_dosha(emphasis: dict) -> str:
    """
    Returns the dosha with second highest emphasis score.
    Used for nuanced personalization.

    Example:
    emphasis = {pitta: 0.774, vata: 0.145, kapha: 0.081}
    returns: "vata"
    """
    sorted_doshas = sorted(
        emphasis, key=emphasis.get, reverse=True
    )
    return sorted_doshas[1]


def interpret_emphasis(emphasis: dict) -> str:
    """
    Returns a human readable interpretation
    of the fuzzy emphasis scores.
    Used in the reasoning panel of the UI.

    Example output:
    "Pitta is strongly dominant (77.4%) with
     minor Vata influence (14.5%)"
    """
    dominant = get_dominant_dosha(emphasis)
    dominant_score = emphasis[dominant] * 100

    secondary = get_secondary_dosha(emphasis)
    secondary_score = emphasis[secondary] * 100

    # Describe dominance level
    if dominant_score >= 70:
        dominance = "strongly dominant"
    elif dominant_score >= 50:
        dominance = "moderately dominant"
    else:
        dominance = "slightly dominant"

    return (
        f"{dominant.title()} is {dominance} "
        f"({dominant_score:.1f}%) with "
        f"minor {secondary.title()} influence "
        f"({secondary_score:.1f}%)"
    )