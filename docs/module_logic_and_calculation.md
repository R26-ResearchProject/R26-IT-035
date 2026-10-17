# Prakriti-Aware Recommendation Module

## Module Logic and Calculation Method

## 1) Purpose

This module generates personalized `diet`, `lifestyle`, and `home_care` recommendations by combining:
- Prakriti identification output
- Skin condition identification output
- User context and safety constraints

The design is knowledge-driven and explainable, not a simple if-else rule chain.

## 2) Input Structure

The module expects JSON with these main sections:
- `user_id`
- `prakriti_result`
  - `dominant_prakriti`
  - `secondary_prakriti`
  - `prakriti_scores` (`vata`, `pitta`, `kapha`)
  - `confidence`
- `skin_result`
  - `predicted_condition`
  - `confidence`
  - `severity`
  - `symptoms`
  - `referral_required`
- `user_context`
  - `age_group`
  - `known_allergies`
  - `pregnancy_status`
  - `preferred_language`

## 3) Knowledge Base Design

The module reads recommendations from JSON files in `data/`:

- `recommendations.json`
  - Stores recommendation items (`rec_id`, `category`, `text`, `tags`, `expert_weight`, `safety_level`, `advice_strength`).
- `mappings.json`
  - Links each recommendation to prakriti, condition, symptoms, and `match_weight`.
- `safety_rules.json`
  - Defines thresholds and blocking logic (confidence cutoffs, severe-case behavior, blocked tags by context).

## 4) End-to-End Module Flow

1. **Load and validate input**
   - Read JSON payload.
   - Check required fields and structures.

2. **Run safety gates**
   - If `referral_required = true`, return referral-first response.
   - If severe condition policy triggers, return referral-first response.
   - If skin confidence is too low, return low-confidence referral response.
   - If prakriti confidence is low, reduce personalization strength (instead of hard-blocking).

3. **Retrieve candidate recommendations**
   - Filter mappings by predicted condition.
   - Match dominant and secondary prakriti.
   - Use symptom overlap to keep relevant candidates.

4. **Compute weighted score**
   - Score each candidate with weighted components (see formula below).

5. **Apply safety filtering**
   - Remove blocked recommendations based on tags and user context.
   - Exclude risky recommendations and context-conflicting candidates.

6. **Rank and diversify**
   - Sort by score (descending).
   - Diversify output across categories when available.

7. **Build explainable output**
   - For each recommendation: include score, reason, matched factors, confidence explanation.
   - Add summary, overall confidence level, safety note, and referral warning.

## 5) Calculation Method

### 5.1 Weighted Scoring Formula

\[
\text{final\_score} =
(\text{prakriti\_match\_score} \times 0.30) +
(\text{condition\_match\_score} \times 0.25) +
(\text{symptom\_match\_score} \times 0.20) +
(\text{module\_confidence\_score} \times 0.10) +
(\text{expert\_weight} \times 0.10) +
(\text{mapping\_match\_weight} \times 0.05)
\]

### 5.2 Score Components

- **`prakriti_match_score`**
  - Derived from `prakriti_scores` for mapped prakriti.
  - Supports mixed prakriti by giving extra emphasis to dominant, and partial bonus for secondary.

- **`condition_match_score`**
  - `1.0` when mapped condition equals predicted condition; else `0.0`.

- **`symptom_match_score`**
  - Uses symptom overlap quality between user symptoms and mapped symptoms.
  - More overlap gives higher score.

- **`module_confidence_score`**
  - Average of:
    - prakriti module confidence
    - skin module confidence

- **`expert_weight`**
  - Practitioner-curated strength from `recommendations.json`.

- **`mapping_match_weight`**
  - Mapping relevance from `mappings.json`.

### 5.3 Severity-Aware Penalty

After weighted scoring, a penalty is applied when severity is higher and recommendation advice is too weak:
- Moderate/severe + weak advice => stronger penalty.
- Moderate/severe + moderate advice => smaller penalty.
- Strong advice => minimal/no penalty.

## 6) Safety-First Behavior

The module prioritizes clinical safety:
- Referral-first output for referral-required or severe-gated cases.
- Low-confidence skin predictions are not over-personalized.
- Risky/blocked recommendations are excluded before final output.

## 7) Output Structure

The module returns:
- `user_id`
- `status` (`success` or `referral_recommended`)
- `recommendation_summary`
- `overall_confidence_level` (`high`, `medium`, `low`)
- `explanation_summary`
- `recommendations_by_category`
  - `diet`
  - `lifestyle`
  - `home_care`
- `safety_note`
- `referral_warning`

## 8) Research Value

This design supports research reporting because it is:
- **Structured** (clear input/output contracts)
- **Explainable** (reasoning included per recommendation)
- **Reproducible** (knowledge-base-driven behavior)
- **Extensible** (JSON now, database/API later)
