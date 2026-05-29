# Question bank (EXPANDED)
QUESTION_BANK = [

    # ======================
    # VATA (10 questions)
    # ======================
    {"id": 1, "text": "Do you have dry skin?", "dosha": "vata", "weight": 2},
    {"id": 2, "text": "Do you feel cold easily?", "dosha": "vata", "weight": 2},
    {"id": 3, "text": "Do you skip meals often?", "dosha": "vata", "weight": 1},
    {"id": 4, "text": "Are you a light sleeper?", "dosha": "vata", "weight": 1},
    {"id": 5, "text": "Do you feel anxious often?", "dosha": "vata", "weight": 1},
    {"id": 6, "text": "Do you have low body weight naturally?", "dosha": "vata", "weight": 1},
    {"id": 7, "text": "Do you have dry lips or hair?", "dosha": "vata", "weight": 1},
    {"id": 8, "text": "Do your hands and feet feel cold often?", "dosha": "vata", "weight": 2},
    {"id": 9, "text": "Do you get tired quickly?", "dosha": "vata", "weight": 1},
    {"id": 10, "text": "Do you have irregular sleep patterns?", "dosha": "vata", "weight": 1},

    # ======================
    # PITTA (10 questions)
    # ======================
    {"id": 11, "text": "Do you feel hot easily?", "dosha": "pitta", "weight": 2},
    {"id": 12, "text": "Do you sweat a lot?", "dosha": "pitta", "weight": 2},
    {"id": 13, "text": "Does your skin get red easily?", "dosha": "pitta", "weight": 1},
    {"id": 14, "text": "Do you feel very hungry if meals are late?", "dosha": "pitta", "weight": 1},
    {"id": 15, "text": "Do you get irritated easily?", "dosha": "pitta", "weight": 1},
    {"id": 16, "text": "Do you prefer cold environments?", "dosha": "pitta", "weight": 1},
    {"id": 17, "text": "Do you experience frequent thirst?", "dosha": "pitta", "weight": 1},
    {"id": 18, "text": "Do you have sensitive skin?", "dosha": "pitta", "weight": 1},
    {"id": 19, "text": "Do you have strong digestion?", "dosha": "pitta", "weight": 2},
    {"id": 20, "text": "Do you feel uncomfortable in hot weather?", "dosha": "pitta", "weight": 2},

    # ======================
    # KAPHA (10 questions)
    # ======================
    {"id": 21, "text": "Do you gain weight easily?", "dosha": "kapha", "weight": 2},
    {"id": 22, "text": "Do you feel sluggish in mornings?", "dosha": "kapha", "weight": 1},
    {"id": 23, "text": "Is your skin oily or smooth?", "dosha": "kapha", "weight": 1},
    {"id": 24, "text": "Is your digestion slow?", "dosha": "kapha", "weight": 2},
    {"id": 25, "text": "Are you calm and steady?", "dosha": "kapha", "weight": 1},
    {"id": 26, "text": "Do you sleep deeply and for long hours?", "dosha": "kapha", "weight": 1},
    {"id": 27, "text": "Do you feel heavy after meals?", "dosha": "kapha", "weight": 1},
    {"id": 28, "text": "Do you have thick or oily hair?", "dosha": "kapha", "weight": 1},
    {"id": 29, "text": "Do you prefer staying still rather than moving?", "dosha": "kapha", "weight": 1},
    {"id": 30, "text": "Do you have a slow but steady energy level?", "dosha": "kapha", "weight": 2},
]


def initialize_scores():
    return {"vata": 0, "pitta": 0, "kapha": 0}


def update_scores(scores, question, answer):
    if answer.lower() == "yes":
        scores[question["dosha"]] += question["weight"]
    return scores


def calculate_confidence(scores):
    total = sum(scores.values()) + 1e-6
    top = max(scores.values())
    return top / total


def get_next_question(scores, asked_ids):
    # find dominant dosha
    dominant = max(scores, key=scores.get)

    for q in QUESTION_BANK:
        if q["id"] not in asked_ids and q["dosha"] == dominant:
            return q

    # fallback: any remaining question
    for q in QUESTION_BANK:
        if q["id"] not in asked_ids:
            return q

    return None