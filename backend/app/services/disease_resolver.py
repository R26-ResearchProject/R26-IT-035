# disease_resolver.py
# Finds disease data from the knowledge base dataset.
# Handles three levels:
# Level 1: Disease is in our 20 validated diseases
# Level 2: Disease matches a category
# Level 3: Disease is completely unknown

import json
from app.services.mongodb_client import get_database
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Load category mappings once when file loads
try:
    with open(
        "app/data/disease_categories/categories_mapping.json"
    ) as f:
        CATEGORIES_DATA = json.load(f)

    # Build a lookup: disease_name -> category data
    # So we can quickly find which category any disease belongs to
    DISEASE_TO_CATEGORY = {}
    for cat in CATEGORIES_DATA.get("categories", []):
        for disease in cat.get("diseases_included", []):
            DISEASE_TO_CATEGORY[disease] = cat

    logger.info("Category mappings loaded successfully")

except Exception as e:
    logger.error(f"Could not load categories file: {e}")
    CATEGORIES_DATA = {}
    DISEASE_TO_CATEGORY = {}


def resolve_disease(disease_id: str) -> dict:
    """
    Resolves disease from dataset.
    Normalizes disease_id before searching.
    """
    # Normalize disease_id
    # Convert spaces to underscores
    # Convert to lowercase
    # Remove special characters
    disease_id = (
        disease_id.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .strip()
    )

    db = get_database()
    # ... rest of existing code

    # LEVEL 1: Check our 20 validated diseases in MongoDB
    disease = db.diseases.find_one(
        {"disease_id": disease_id},
        {"_id": 0}  # Exclude MongoDB internal ID
    )

    if disease:
        logger.info(
            f"Level 1 resolution for: {disease_id}"
        )
        disease["explanation_level"] = "validated"
        disease["level_number"] = 1
        return disease

    # LEVEL 2: Check category mappings
    category = DISEASE_TO_CATEGORY.get(disease_id)

    if category:
        logger.info(
            f"Level 2 category resolution for: {disease_id} "
            f"-> {category['category_id']}"
        )
        return {
            "disease_id": disease_id,
            "name": disease_id.replace("_", " ").title(),
            "category": category["category_id"],
            "western": {
                "description": f"a {category['category_id']} skin condition",
                "symptoms": ["skin changes", "discomfort"],
                "causes": ["various factors"],
                "triggers": ["varies by individual"],
                "complications": ["consult a doctor for details"]
            },
            "ayurvedic": {
                "sanskrit_name": "Kushtha variant",
                "ayurveda_meaning": "skin disorder",
                "primary_dosha": category["primary_dosha"],
                "secondary_dosha": "varies",
                "classical_text": "General Ayurvedic principles",
                "dosha_cause": f"imbalance in {category['primary_dosha']} dosha"
            },
            "dosha_aggravation": category["dosha_aggravation"],
            "prevention": ["consult a healthcare provider"],
            "dosha_advice": {
                "vata": "follow Vata-balancing practices",
                "pitta": "follow Pitta-balancing practices",
                "kapha": "follow Kapha-balancing practices"
            },
            "explanation_level": "category",
            "level_number": 2
        }

    # LEVEL 3: Completely unknown disease
    logger.warning(
        f"Level 3 unknown disease: {disease_id}"
    )
    return {
        "disease_id": disease_id,
        "name": disease_id.replace("_", " ").title(),
        "category": "skin condition",
        "western": {
            "description": "a skin condition",
            "symptoms": ["skin changes"],
            "causes": ["various factors"],
            "triggers": ["varies by individual"],
            "complications": ["consult a doctor for details"]
        },
        "ayurvedic": {
            "sanskrit_name": "Kushtha",
            "ayurveda_meaning": "skin disorder",
            "primary_dosha": "pitta",
            "secondary_dosha": "vata",
            "classical_text": "General Ayurvedic principles",
            "dosha_cause": "dosha imbalance affecting skin"
        },
        "dosha_aggravation": {
            "vata": 0.33,
            "pitta": 0.33,
            "kapha": 0.33
        },
        "prevention": ["consult a healthcare provider"],
        "dosha_advice": {
            "vata": "follow Vata-balancing practices",
            "pitta": "follow Pitta-balancing practices",
            "kapha": "follow Kapha-balancing practices"
        },
        "explanation_level": "general",
        "level_number": 3
    }