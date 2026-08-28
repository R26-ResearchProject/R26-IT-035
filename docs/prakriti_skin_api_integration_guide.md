# Prakriti and Skin Module API Integration Guide

## How to Feed External Module Outputs Into the Recommendation Module

## 1) Goal

This document explains:
- What the **Prakriti module** should provide
- What the **Skin module** should provide
- How to merge those outputs and send them to this recommendation module

The recommendation module expects one combined JSON payload.  
For now, you can enter values manually. Later, these values should come from API responses.

## 2) Required Final Input for Recommendation Module

The recommendation API expects this shape:

```json
{
  "user_id": "U001",
  "prakriti_result": {
    "dominant_prakriti": "Vata",
    "secondary_prakriti": "Pitta",
    "prakriti_scores": {
      "vata": 0.72,
      "pitta": 0.20,
      "kapha": 0.08
    },
    "confidence": 0.81
  },
  "skin_result": {
    "predicted_condition": "Eczema",
    "confidence": 0.87,
    "severity": "mild",
    "symptoms": ["dryness", "itching", "redness"],
    "referral_required": false
  },
  "user_context": {
    "age_group": "adult",
    "known_allergies": [],
    "pregnancy_status": false,
    "preferred_language": "English"
  }
}
```

## 3) What Prakriti Module Should Provide

Minimum required fields:
- `dominant_prakriti` (string: `Vata`, `Pitta`, `Kapha`)
- `secondary_prakriti` (string)
- `prakriti_scores` (object with numeric `vata`, `pitta`, `kapha`, usually 0 to 1)
- `confidence` (number, 0 to 1)

Example Prakriti API response:

```json
{
  "user_id": "U001",
  "dominant_prakriti": "Vata",
  "secondary_prakriti": "Pitta",
  "scores": {
    "vata": 0.72,
    "pitta": 0.20,
    "kapha": 0.08
  },
  "confidence": 0.81
}
```

Mapping to recommendation payload:
- `scores` -> `prakriti_scores`
- Keep confidence as-is

## 4) What Skin Module Should Provide

Minimum required fields:
- `predicted_condition` (string, e.g., `Eczema`, `Acne`, `Dry Skin`, `Psoriasis`, `Fungal Infection`)
- `confidence` (number, 0 to 1)
- `severity` (`mild` / `moderate` / `severe`)
- `symptoms` (array of strings)
- `referral_required` (boolean)

Example Skin API response:

```json
{
  "user_id": "U001",
  "prediction": "Eczema",
  "confidence": 0.87,
  "severity": "mild",
  "symptoms": ["dryness", "itching", "redness"],
  "referral_required": false
}
```

Mapping to recommendation payload:
- `prediction` -> `predicted_condition`
- Other fields map directly

## 5) Combine Both APIs Into One Payload

You will typically call both services, then merge:
- Prakriti result -> `prakriti_result`
- Skin result -> `skin_result`
- User profile data -> `user_context`

Then send merged payload to:
- `POST /api/recommend`

## 6) Example Integration Flow

1. Get Prakriti API result
2. Get Skin API result
3. Build unified JSON payload
4. Send payload to recommendation module API
5. Render grouped output (`diet`, `lifestyle`, `home_care`)

## 7) Example End-to-End Request/Response

### Request to recommendation module

```http
POST /api/recommend?top_k=6
Content-Type: application/json
```

```json
{
  "user_id": "U001",
  "prakriti_result": {
    "dominant_prakriti": "Vata",
    "secondary_prakriti": "Pitta",
    "prakriti_scores": {
      "vata": 0.72,
      "pitta": 0.20,
      "kapha": 0.08
    },
    "confidence": 0.81
  },
  "skin_result": {
    "predicted_condition": "Eczema",
    "confidence": 0.87,
    "severity": "mild",
    "symptoms": ["dryness", "itching", "redness"],
    "referral_required": false
  },
  "user_context": {
    "age_group": "adult",
    "known_allergies": [],
    "pregnancy_status": false,
    "preferred_language": "English"
  }
}
```

### Typical response fields
- `status`
- `overall_confidence_level`
- `recommendation_summary`
- `recommendations_by_category`
- `safety_note`
- `referral_warning`

## 8) Validation Checklist Before Sending

- `user_id` is present
- Prakriti scores include all three keys: `vata`, `pitta`, `kapha`
- Confidence values are numeric and in 0-1 range
- Severity is one of `mild/moderate/severe`
- Symptoms array is non-empty
- `referral_required` is boolean

## 9) Error Handling Recommendations

If one upstream module fails:
- Return a clear UI message: "Prakriti/Skin module unavailable"
- Allow retry
- Do not send partial invalid payload to recommendation API

If confidence is low:
- You can still send data, but recommendation module may return referral-oriented output based on safety rules.

## 10) Future Production Notes

- Keep this payload contract stable as shared API schema.
- Add versioning later, e.g., `schema_version: "1.0"`.
- Add auth and request signing between modules.
- Add request/response logging for traceability in research experiments.
