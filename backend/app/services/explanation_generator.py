# explanation_generator.py
# PURPOSE: Main orchestrator of Novelty 3.
# Connects all services together.
# Receives disease + Prakriti + user context
# Returns complete dual explanation.
#
# FLOW:
# 1. Safety check first
# 2. Resolve disease from dataset
# 3. Get Western explanation
# 4. Run fuzzy engine
# 5. Compose all templates with context
# 6. Build reasoning trace
# 7. Log to MongoDB
# 8. Return complete response

from app.services.safety_checker import (
    check_disease_safety
)
from app.services.disease_resolver import resolve_disease
from app.services.western_retriever import (
    get_western_explanation
)
from app.services.fuzzy_engine import (
    compute_emphasis,
    get_dominant_dosha,
    get_secondary_dosha,
    interpret_emphasis
)
from app.services.template_composer import (
    compose_full_explanation,
    fill_western_template
)
from app.services.mongodb_client import get_database
from app.utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)


def generate_explanation(
    disease_id: str,
    confidence: float,
    prakriti: dict,
    user_context: dict = None  # Optional context
) -> dict:
    """
    Generates complete dual explanation.

    Parameters:
    - disease_id: from Novelty 2 (e.g. "eczema")
    - confidence: Novelty 2 confidence score
    - prakriti: from Novelty 1
      e.g. {vata: 0.30, pitta: 0.60, kapha: 0.10}
    - user_context: optional personal info
      e.g. {age_group: "adult", pregnancy_status: false}

    Returns:
    Complete explanation dict for frontend
    """

    logger.info(
        f"Generating explanation for: {disease_id} "
        f"confidence: {confidence} "
        f"context: {user_context}"
    )

    # ─────────────────────────────────────────
    # STEP 1: SAFETY CHECK
    # Runs FIRST before everything else.
    # Blocks dangerous diseases immediately.
    # Returns referral message instead of explanation.
    # ─────────────────────────────────────────
    safety_response = check_disease_safety(disease_id)

    if safety_response:
        logger.warning(
            f"Safety block: {disease_id}"
        )
        # Return safety referral — no explanation at all
        return {
            "type": "safety_referral",
            "disease_id": disease_id,
            "safety": safety_response,
            "western": None,
            "ayurvedic": None,
            "personalized": None,
            "prevention": None,
            "reasoning": None
        }

    # ─────────────────────────────────────────
    # STEP 2: RESOLVE DISEASE FROM DATASET
    # Finds disease in knowledge base.
    # Level 1: your 20 validated diseases
    # Level 2: category-based mapping
    # Level 3: unknown disease fallback
    # ─────────────────────────────────────────
    disease_data = resolve_disease(disease_id)
    explanation_level = disease_data.get(
        "explanation_level", "general"
    )

    logger.info(
        f"Disease resolved: {explanation_level}"
    )

    # ─────────────────────────────────────────
    # STEP 3: GET WESTERN EXPLANATION
    # For validated diseases (your 20):
    #   Use your dataset template — high quality
    # For unknown diseases:
    #   Use external API (MedlinePlus/Wikipedia)
    # ─────────────────────────────────────────
    if explanation_level == "validated":
        # Generate from your validated dataset
        # This is high quality content from
        # DermNet NZ and Mayo Clinic sources
        logger.info(
            f"Using dataset template: {disease_id}"
        )
        western_text = fill_western_template(
            disease_data,
            user_context  # Pass context for allergy alert
        )
        western_result = {
            "explanation": western_text,
            "source": "Validated Medical Knowledge Base",
            "source_detail": (
                "Generated from DermNet NZ and "
                "Mayo Clinic validated dataset"
            ),
            "quality": "high",
            "method": "dataset_template"
        }
    else:
        # Use external API for unknown diseases
        # ChromaDB → MedlinePlus → Wikipedia → Fallback
        logger.info(
            f"Using API retrieval: {disease_id}"
        )
        western_result = get_western_explanation(
            disease_id
        )

    # ─────────────────────────────────────────
    # STEP 4: RUN FUZZY ENGINE
    # Core research contribution.
    # Computes how this disease affects THIS user
    # specifically based on their Prakriti scores.
    # Same disease = different scores for different users
    # ─────────────────────────────────────────
    fuzzy_emphasis = compute_emphasis(
        disease_data, prakriti
    )
    dominant_dosha = get_dominant_dosha(fuzzy_emphasis)
    secondary_dosha = get_secondary_dosha(fuzzy_emphasis)
    emphasis_interpretation = interpret_emphasis(
        fuzzy_emphasis
    )

    logger.info(
        f"Fuzzy: {dominant_dosha} dominant "
        f"scores: {fuzzy_emphasis}"
    )

    # ─────────────────────────────────────────
    # STEP 5: COMPOSE ALL EXPLANATIONS
    # Calls template_composer.py
    # All context (pregnancy, age, allergies) is
    # merged directly into the three explanations
    # No separate fields created
    # ─────────────────────────────────────────
    composed = compose_full_explanation(
        disease_data,
        fuzzy_emphasis,
        user_context  # Pass for pregnancy/age/allergy
    )

    # ─────────────────────────────────────────
    # STEP 6: BUILD REASONING TRACE
    # Records all decisions made.
    # Powers the Show Reasoning panel in UI.
    # This is the explainability layer.
    # ─────────────────────────────────────────
    reasoning = {
        "fuzzy_scores": fuzzy_emphasis,
        "dominant_dosha": dominant_dosha,
        "secondary_dosha": secondary_dosha,
        "emphasis_interpretation": emphasis_interpretation,
        "explanation_level": explanation_level,
        "disease_primary_dosha": disease_data[
            "ayurvedic"
        ]["primary_dosha"],
        "western_source": western_result["source"],
        "western_quality": western_result["quality"],
        "western_method": western_result["method"],
        "context_applied": {
            "pregnancy": (
                user_context.get("pregnancy_status", False)
                if user_context else False
            ),
            "age_group": (
                user_context.get("age_group", "adult")
                if user_context else "adult"
            ),
            "allergies_checked": (
                len(user_context.get(
                    "known_allergies", []
                )) > 0
                if user_context else False
            )
        }
    }

    # ─────────────────────────────────────────
    # STEP 7: LOG TO MONGODB
    # Every request logged for evaluation.
    # Used to measure accuracy in thesis.
    # ─────────────────────────────────────────
    try:
        db = get_database()
        db.reasoning_logs.insert_one({
            "timestamp": datetime.utcnow(),
            "disease_id": disease_id,
            "confidence": confidence,
            "prakriti_input": prakriti,
            "fuzzy_emphasis": fuzzy_emphasis,
            "dominant_dosha": dominant_dosha,
            "explanation_level": explanation_level,
            "western_method": western_result["method"],
            "western_quality": western_result["quality"],
            "user_context": user_context
        })
    except Exception as e:
        # Log error but never stop the response
        logger.error(f"Could not save log: {e}")

    # ─────────────────────────────────────────
    # STEP 8: RETURN COMPLETE RESPONSE
    # Sent to React frontend for display.
    # ─────────────────────────────────────────
    return {
        "type": "full_explanation",
        "disease_id": disease_id,
        "disease_name": disease_data["name"],
        "category": disease_data.get("category", ""),
        "confidence": confidence,
        "explanation_level": explanation_level,

        # Western explanation
        # Includes allergy alert if applicable
        "western": {
            "explanation": western_result["explanation"],
            "source": western_result["source"],
            "source_detail": western_result.get(
                "source_detail", ""
            ),
            "quality": western_result["quality"],
            "method": western_result["method"]
        },

        # Ayurvedic explanation
        # Includes pregnancy + age notes if applicable
        "ayurvedic": {
            "explanation": composed["ayurvedic"],
            "sanskrit_name": disease_data[
                "ayurvedic"
            ]["sanskrit_name"],
            "ayurveda_meaning": disease_data[
                "ayurvedic"
            ]["ayurveda_meaning"],
            "primary_dosha": disease_data[
                "ayurvedic"
            ]["primary_dosha"],
            "classical_text": disease_data[
                "ayurvedic"
            ]["classical_text"]
        },

        # Personalized explanation
        # Driven by fuzzy engine
        # Includes age advice + pregnancy warning
        "personalized": composed["personalized"],

        

        # Reasoning trace for explainability
        "reasoning": reasoning
    }
