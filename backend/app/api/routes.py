from fastapi import APIRouter, UploadFile, File, Form
import cv2
import numpy as np
import json
from datetime import datetime, timezone

from app.services.prakriti_service import (
    predict_ml_scores,
    finalize_prakriti
)
from app.db.mongodb import save_result
from app.utils.validation import (
    validate_file,
    check_blur,
    check_lighting
)


router = APIRouter()


@router.post("/prakriti/analyze")
async def analyze(
    user_id: str = Form(...),
    image: UploadFile = File(...),
    answers: str = Form(...)
):

    # -------------------------
    # USER ID VALIDATION
    # -------------------------

    user_id = user_id.strip()

    if not user_id:
        return {
            "error": "User ID is required"
        }

    # -------------------------
    # FILE TYPE VALIDATION
    # -------------------------

    valid, error = validate_file(image)

    if not valid:
        return {
            "error": error
        }

    contents = await image.read()

    print("File received:", image.filename)
    print("Content type:", image.content_type)

    # -------------------------
    # EMPTY FILE VALIDATION
    # -------------------------

    if not contents:
        return {
            "error": "Uploaded image is empty"
        }

    # -------------------------
    # FILE SIZE VALIDATION
    # -------------------------

    if len(contents) > 5 * 1024 * 1024:
        return {
            "error": "File too large. Maximum file size is 5 MB."
        }

    # -------------------------
    # DECODE IMAGE
    # -------------------------

    try:
        nparr = np.frombuffer(
            contents,
            dtype=np.uint8
        )

        img = cv2.imdecode(
            nparr,
            cv2.IMREAD_COLOR
        )

    except Exception as exc:
        print("Image decoding error:", exc)

        return {
            "error": "Unable to process the uploaded image"
        }

    print(
        "Image shape:",
        img.shape if img is not None else "Invalid image"
    )

    if img is None:
        return {
            "error": "Invalid image file"
        }

    # -------------------------
    # IMAGE QUALITY VALIDATION
    # -------------------------

    valid, error = check_blur(img)

    if not valid:
        return {
            "error": error
        }

    valid, error = check_lighting(img)

    if not valid:
        return {
            "error": error
        }

    # -------------------------
    # QUESTIONNAIRE VALIDATION
    # -------------------------

    try:
        questionnaire_data = json.loads(answers)

        if not isinstance(questionnaire_data, dict):
            return {
                "error": "Questionnaire answers must be a JSON object"
            }

        q_scores = {
            "vata": float(
                questionnaire_data.get("vata", 0)
            ),
            "pitta": float(
                questionnaire_data.get("pitta", 0)
            ),
            "kapha": float(
                questionnaire_data.get("kapha", 0)
            )
        }

        # Reject NaN and infinite values
        if not all(
            np.isfinite(value)
            for value in q_scores.values()
        ):
            return {
                "error": "Invalid questionnaire values"
            }

        # Reject negative scores
        if any(
            value < 0
            for value in q_scores.values()
        ):
            return {
                "error": "Questionnaire values cannot be negative"
            }

        # All scores cannot be zero
        if sum(q_scores.values()) <= 0:
            return {
                "error": "Questionnaire scores cannot all be zero"
            }

    except (json.JSONDecodeError, TypeError, ValueError):
        return {
            "error": "Invalid questionnaire format"
        }

    # -------------------------
    # FACIAL ML PREDICTION
    # -------------------------

    try:
        # This now returns:
        # {
        #     "scores": {...},
        #     "module_analysis": {...}
        # }
        ml_result = predict_ml_scores(img)

    except ValueError as exc:
        print("ML input error:", exc)

        return {
            "error": str(exc)
        }

    except Exception as exc:
        print("ML prediction error:", exc)

        return {
            "error": "Unable to complete facial analysis"
        }

    if ml_result is None:
        return {
            "error": "Face not detected. Please upload a clear front-facing image."
        }

    # -------------------------
    # FINAL FUSION
    # -------------------------

    try:
        result = finalize_prakriti(
            ml_result,
            q_scores
        )

    except Exception as exc:
        print("Fusion error:", exc)

        return {
            "error": "Unable to generate the final Prakriti result"
        }

    if result is None:
        return {
            "error": "Unable to generate the Prakriti result"
        }

    # -------------------------
    # SAVE EXISTING FIELDS
    # TO MONGODB
    # -------------------------

    # The database structure is unchanged.
    # module_analysis and ai_explanation are only
    # returned to the frontend.

    db_data = {
        "user_id": user_id,
        "dominant_prakriti": result[
            "dominant_prakriti"
        ],
        "secondary_prakriti": result[
            "secondary_prakriti"
        ],
        "prakriti_scores": result[
            "prakriti_scores"
        ],
        "confidence": result[
            "confidence"
        ],
        "timestamp": datetime.now(timezone.utc)
    }

    try:
        inserted_id = save_result(db_data)

    except Exception as exc:
        print("Database saving error:", exc)

        return {
            "error": "Prediction completed, but the result could not be saved"
        }

    # -------------------------
    # FINAL API RESPONSE
    # -------------------------

    return {
        "success": True,
        "user_id": user_id,

        # Includes:
        # - dominant_prakriti
        # - secondary_prakriti
        # - prakriti_scores
        # - confidence
        # - module_analysis
        # - ai_explanation
        "data": result,

        "db_id": str(inserted_id)
    }