from fastapi import APIRouter
from app.services.questionnaire import (
    initialize_scores,
    update_scores,
    calculate_confidence,
    get_next_question,
    QUESTION_BANK
)

router = APIRouter()

# -------------------------
# START QUESTIONNAIRE
# -------------------------
@router.get("/questionnaire/start")
def start_questionnaire():

    scores = initialize_scores()

    # first 3 questions (1 per dosha)
    starter_questions = [
        next(q for q in QUESTION_BANK if q["dosha"] == "vata" and q["weight"] == 2),
        next(q for q in QUESTION_BANK if q["dosha"] == "pitta" and q["weight"] == 2),
        next(q for q in QUESTION_BANK if q["dosha"] == "kapha" and q["weight"] == 2),
    ]

    return {
        "scores": scores,
        "questions": starter_questions,
        "asked_ids": [q["id"] for q in starter_questions]
    }


# -------------------------
# NEXT QUESTION (ADAPTIVE)
# -------------------------
@router.post("/questionnaire/next")
def next_question(payload: dict):

    scores = payload["scores"]
    asked_ids = payload["asked_ids"]
    last_question = payload["last_question"]
    answer = payload["answer"]

    # update scores
    scores = update_scores(scores, last_question, answer)

    confidence = calculate_confidence(scores)

    # STOP CONDITION
    if len(asked_ids) >= 8 or (len(asked_ids) >= 6 and confidence >= 0.55):
        return {
            "done": True,
            "scores": scores,
            "confidence": confidence
        }

    # get next adaptive question
    next_q = get_next_question(scores, asked_ids)

    if next_q:
        asked_ids.append(next_q["id"])

    return {
        "done": False,
        "next_question": next_q,
        "scores": scores,
        "asked_ids": asked_ids,
        "confidence": confidence
    }