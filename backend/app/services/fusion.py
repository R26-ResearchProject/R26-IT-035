def fuse_scores(ml_scores, q_scores):
 
    # -------------------------
    # Normalize questionnaire scores
    # Example:
    # Vata = 4, Pitta = 2, Kapha = 4
    # Total = 10
    #
    # Vata  = 4 / 10 = 0.4
    # Pitta = 2 / 10 = 0.2
    # Kapha = 4 / 10 = 0.4
    # -------------------------
    
    # Normalize questionnaire scores
    total_q = sum(q_scores.values()) + 1e-6
    q_norm = {k: v / total_q for k, v in q_scores.items()}
    
    
    # -------------------------
    # Weighted Fusion
    #
    # 30% → ML Prediction
    # 70% → Questionnaire
    #
    # Example:
    #
    # ML Vata Score = 0.60
    # Questionnaire Vata Score = 0.80
    #
    # Final Vata =
    # (0.3 × 0.60) + (0.7 × 0.80)
    # = 0.18 + 0.56
    # = 0.74
    # -------------------------

    
    final = {
        "vata": 0.3 * ml_scores["vata"] + 0.7 * q_norm["vata"],
        "pitta": 0.3 * ml_scores["pitta"] + 0.7 * q_norm["pitta"],
        "kapha": 0.3 * ml_scores["kapha"] + 0.7 * q_norm["kapha"],
    }

    # -------------------------
    # Normalize Final Scores Again
    #
    # Example:
    #
    # Vata  = 0.74
    # Pitta = 0.18
    # Kapha = 0.08
    #
    # Total = 1.00
    #
    # This creates proper probability-like
    # score distribution
    # -------------------------
    # Normalize again
    
    total = sum(final.values()) + 1e-6
    final = {k: v / total for k, v in final.items()}

    return final