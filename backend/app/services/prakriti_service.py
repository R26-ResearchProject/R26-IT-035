# Import facial feature extraction
from app.services.feature_extraction import extract_features

# Import final facial + questionnaire fusion
from app.services.fusion import fuse_scores

# Import modular analysis functions
from app.services.module_analysis import (
    create_module_analysis,
    combine_facial_modules,
    create_questionnaire_analysis,
    create_ai_explanation
)


# =========================================================
# FACIAL PRAKRITI PREDICTION
# =========================================================

def predict_ml_scores(image):
    """
    Facial prediction flow:

    Image
      ↓
    Extract 20 facial features
      ↓
    Geometry / Texture / Colour / Symmetry
      ↓
    Each module calculates:
        Vata
        Pitta
        Kapha
        Confidence
      ↓
    Confidence-aware module fusion
      ↓
    Final facial Vata / Pitta / Kapha scores

    The function name predict_ml_scores is kept
    so existing routes do not need to change.
    """

    # -----------------------------------------------------
    # 1. EXTRACT 20 FACIAL FEATURES
    # -----------------------------------------------------

    features = extract_features(
        image
    )

    # Stop if no face detected
    if features is None:
        return None


    # -----------------------------------------------------
    # 2. VALIDATE FEATURE COUNT
    # -----------------------------------------------------

    if len(features) != 20:

        raise ValueError(
            f"Expected 20 facial features, "
            f"but received {len(features)}"
        )


    # -----------------------------------------------------
    # 3. CREATE FOUR FACIAL MODULES
    # -----------------------------------------------------

    facial_modules = (
        create_module_analysis(
            features
        )
    )


    if not facial_modules:

        return None


    # -----------------------------------------------------
    # 4. COMBINE MODULES USING CONFIDENCE
    # -----------------------------------------------------
    #
    # Geometry
    # Texture
    # Colour
    # Symmetry
    #
    # Each module's scores are weighted
    # using that module's confidence.
    # -----------------------------------------------------

    facial_scores = (
        combine_facial_modules(
            facial_modules
        )
    )


    # -----------------------------------------------------
    # 5. RETURN FACIAL RESULT
    # -----------------------------------------------------

    return {

        "vata": float(
            facial_scores["vata"]
        ),

        "pitta": float(
            facial_scores["pitta"]
        ),

        "kapha": float(
            facial_scores["kapha"]
        ),

        # Keep module details for frontend
        # explanation.
        "_module_analysis":
            facial_modules
    }


# =========================================================
# FINAL PRAKRITI DECISION
# =========================================================

def finalize_prakriti(
    ml_scores,
    q_scores
):
    """
    Final system flow:

    Facial module fusion
           +
    Questionnaire scores
           ↓
    Existing fusion logic
           ↓
    Final Vata / Pitta / Kapha
           ↓
    Dominant
    Secondary
    Overall Confidence
    """


    # -----------------------------------------------------
    # 1. GET FACIAL MODULE DETAILS
    # -----------------------------------------------------

    facial_modules = (
        ml_scores.get(
            "_module_analysis",
            {}
        )
    )


    # -----------------------------------------------------
    # 2. GET COMBINED FACIAL SCORES
    # -----------------------------------------------------
    #
    # These scores were already generated
    # by combining:
    #
    # Geometry
    # Texture
    # Colour
    # Symmetry
    #
    # using module confidence.
    # -----------------------------------------------------

    facial_scores = {

        "vata":
            float(
                ml_scores["vata"]
            ),

        "pitta":
            float(
                ml_scores["pitta"]
            ),

        "kapha":
            float(
                ml_scores["kapha"]
            )
    }


    # -----------------------------------------------------
    # 3. COMBINE FACIAL + QUESTIONNAIRE
    # -----------------------------------------------------
    #
    # Your existing fusion.py controls
    # the final weighting.
    #
    # Example:
    #
    # Facial = 30%
    # Questionnaire = 70%
    # -----------------------------------------------------

    final_scores = fuse_scores(
        facial_scores,
        q_scores
    )


    # -----------------------------------------------------
    # 4. ROUND FINAL SCORES
    # -----------------------------------------------------

    final_scores = {

        "vata": round(
            float(
                final_scores["vata"]
            ),
            2
        ),

        "pitta": round(
            float(
                final_scores["pitta"]
            ),
            2
        ),

        "kapha": round(
            float(
                final_scores["kapha"]
            ),
            2
        )
    }


    # -----------------------------------------------------
    # 5. SORT FINAL SCORES
    # -----------------------------------------------------

    sorted_scores = sorted(

        final_scores.items(),

        key=lambda item:
            item[1],

        reverse=True
    )


    # -----------------------------------------------------
    # 6. DOMINANT PRAKRITI
    # -----------------------------------------------------

    dominant = (
        sorted_scores[0][0]
    )


    # -----------------------------------------------------
    # 7. SECONDARY PRAKRITI
    # -----------------------------------------------------

    secondary = (
        sorted_scores[1][0]
    )


    # -----------------------------------------------------
    # 8. OVERALL CONFIDENCE
    # -----------------------------------------------------
    #
    # Highest final fused score becomes
    # the overall confidence.
    # -----------------------------------------------------

    confidence = round(
        float(
            sorted_scores[0][1]
        ),
        2
    )


    # -----------------------------------------------------
    # 9. QUESTIONNAIRE MODULE
    # -----------------------------------------------------

    questionnaire_module = (
        create_questionnaire_analysis(
            q_scores
        )
    )


    # -----------------------------------------------------
    # 10. COMBINE MODULE ANALYSIS FOR EXPLANATION
    # -----------------------------------------------------

    module_analysis = {

        **facial_modules,

        "questionnaire":
            questionnaire_module
    }


    # -----------------------------------------------------
    # 11. GENERATE AI EXPLANATION
    # -----------------------------------------------------

    ai_explanation = (
        create_ai_explanation(

            dominant.capitalize(),

            secondary.capitalize(),

            confidence,

            module_analysis
        )
    )


    # -----------------------------------------------------
    # 12. FINAL RESPONSE
    # -----------------------------------------------------

    return {

        "dominant_prakriti":
            dominant.capitalize(),

        "secondary_prakriti":
            secondary.capitalize(),

        "prakriti_scores":
            final_scores,

        "confidence":
            confidence,

        "module_analysis":
            module_analysis,

        "ai_explanation":
            ai_explanation
    }