"""Core recommendation engine: retrieve, score, filter, rank, explain."""

from typing import Any, Dict, List

from explainability import (
    build_explanation_summary,
    build_confidence_explanation,
    build_recommendation_reason,
    build_summary,
    default_safety_note,
    referral_only_payload,
)
from safety_filter import apply_recommendation_safety_filters, evaluate_global_safety
from scoring import compute_candidate_score, rank_candidates


class RecommendationEngine:
    """Data-driven recommendation engine for Ayurvedic personalization."""

    def __init__(self, knowledge_base: Dict[str, Any]) -> None:
        self.recommendations = knowledge_base["recommendations"]
        self.mappings = knowledge_base["mappings"]
        self.safety_rules = knowledge_base["safety_rules"]
        self._recommendation_by_id = {item["rec_id"]: item for item in self.recommendations}

    def generate(self, user_input: Dict[str, Any], top_k: int = 5) -> Dict[str, Any]:
        """Generate explainable and safety-aware recommendation output."""
        return self.analyze(user_input, top_k)["result"]

    def analyze(self, user_input: Dict[str, Any], top_k: int = 5) -> Dict[str, Any]:
        """Run the full pipeline and return the response plus the reasoning trail.

        The reasoning trail (all scored candidates, excluded candidates, and which
        ids made the final cut) is what the follow-up Q&A layer inspects to answer
        "why not X" / "what if" questions without re-guessing engine internals.
        """
        safety_state = evaluate_global_safety(user_input, self.safety_rules)
        if not safety_state["allow_recommendations"]:
            return {
                "result": referral_only_payload(user_input["user_id"], safety_state["safety_messages"]),
                "all_scored": [],
                "exclusions": [],
                "selected_ids": [],
                "blocked": True,
            }

        candidates = self._retrieve_candidates(user_input)
        scored = self._score_candidates(user_input, candidates, safety_state["personalization_factor"])
        safe_scored, caution_messages, exclusions = apply_recommendation_safety_filters(
            scored, user_input, self.safety_rules
        )
        ranked = rank_candidates(safe_scored)
        diversified = self._diversify_categories(ranked, top_k)
        explained = self._add_explainability(user_input, diversified)

        safety_note_parts = [default_safety_note()]
        safety_note_parts.extend(safety_state["safety_messages"])
        safety_note_parts.extend(caution_messages)

        result = {
            "user_id": user_input["user_id"],
            "status": "success",
            "recommendation_summary": build_summary(user_input, len(explained)),
            "overall_confidence_level": self._overall_confidence_level(user_input),
            "explanation_summary": build_explanation_summary(user_input, len(explained)),
            "recommendations_by_category": self._group_by_category(explained),
            "safety_note": " ".join(safety_note_parts).strip(),
            "referral_warning": self._referral_warning(user_input),
        }

        return {
            "result": result,
            "all_scored": ranked,
            "exclusions": exclusions,
            "selected_ids": [item["rec_id"] for item in diversified],
            "blocked": False,
        }

    def _retrieve_candidates(self, user_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve candidate mappings by condition and prakriti relationships."""
        skin_condition = user_input["skin_result"]["predicted_condition"].lower()
        dominant = user_input["prakriti_result"]["dominant_prakriti"].lower()
        secondary = user_input["prakriti_result"]["secondary_prakriti"].lower()
        user_symptoms = {symptom.lower() for symptom in user_input["skin_result"]["symptoms"]}

        candidates: List[Dict[str, Any]] = []
        for mapping in self.mappings:
            if mapping["condition"].lower() != skin_condition:
                continue

            mapping_prakriti = mapping["prakriti"].lower()
            mapping_symptoms = {symptom.lower() for symptom in mapping.get("symptoms", [])}

            if mapping_prakriti not in {dominant, secondary} and not mapping_symptoms.intersection(user_symptoms):
                continue

            recommendation = self._recommendation_by_id.get(mapping["rec_id"])
            if not recommendation:
                continue

            candidates.append({"recommendation": recommendation, "mapping": mapping})

        return candidates

    def _score_candidates(
        self, user_input: Dict[str, Any], candidates: List[Dict[str, Any]], personalization_factor: float
    ) -> List[Dict[str, Any]]:
        """Score each candidate and flatten payload for downstream ranking/filtering."""
        scored_items: List[Dict[str, Any]] = []
        for candidate in candidates:
            recommendation = candidate["recommendation"]
            mapping = candidate["mapping"]
            score_bundle = compute_candidate_score(user_input, recommendation, mapping)
            adjusted_score = round(score_bundle["final_score"] * personalization_factor, 4)

            scored_items.append(
                {
                    **recommendation,
                    "score": adjusted_score,
                    "score_components": score_bundle["score_components"],
                    "matched_factors": {
                        "prakriti": mapping["prakriti"],
                        "condition": mapping["condition"],
                        "symptoms": self._matched_symptoms(user_input, mapping),
                    },
                }
            )

        return scored_items

    def _diversify_categories(self, ranked_items: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """Promote category diversity (diet/lifestyle/home_care) when available."""
        required_categories = ["diet", "lifestyle", "home_care"]
        selected: List[Dict[str, Any]] = []
        used_ids = set()

        for category in required_categories:
            for item in ranked_items:
                if item["category"] == category and item["rec_id"] not in used_ids:
                    selected.append(item)
                    used_ids.add(item["rec_id"])
                    break

        for item in ranked_items:
            if len(selected) >= top_k:
                break
            if item["rec_id"] in used_ids:
                continue
            selected.append(item)
            used_ids.add(item["rec_id"])

        return selected[:top_k]

    def _add_explainability(self, user_input: Dict[str, Any], items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create final response records with reason and confidence explanation."""
        explained: List[Dict[str, Any]] = []
        for item in items:
            explained.append(
                {
                    "rec_id": item["rec_id"],
                    "category": item["category"],
                    "title": item["title"],
                    "text": item["text"],
                    "score": item["score"],
                    "reason": build_recommendation_reason(item),
                    "matched_factors": item["matched_factors"],
                    "confidence_explanation": build_confidence_explanation(
                        user_input, item["score_components"]
                    ),
                }
            )
        return explained

    @staticmethod
    def _group_by_category(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group recommendations by category in final output."""
        grouped = {"diet": [], "lifestyle": [], "home_care": []}
        for item in items:
            category = item["category"]
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(item)
        return grouped

    @staticmethod
    def _overall_confidence_level(user_input: Dict[str, Any]) -> str:
        """Map combined module confidence to high/medium/low."""
        prakriti_conf = float(user_input["prakriti_result"]["confidence"])
        skin_conf = float(user_input["skin_result"]["confidence"])
        combined = (prakriti_conf + skin_conf) / 2.0
        if combined >= 0.8:
            return "high"
        if combined >= 0.65:
            return "medium"
        return "low"

    @staticmethod
    def _referral_warning(user_input: Dict[str, Any]) -> str:
        """Return referral warning hint when severity is high."""
        severity = str(user_input["skin_result"]["severity"]).lower()
        if severity in {"moderate", "severe"}:
            return "Consult a qualified dermatologist/Ayurvedic physician if symptoms persist or worsen."
        return ""

    @staticmethod
    def _matched_symptoms(user_input: Dict[str, Any], mapping: Dict[str, Any]) -> List[str]:
        """Return symptom intersection for explainability."""
        user_symptoms = {symptom.lower() for symptom in user_input["skin_result"]["symptoms"]}
        mapped_symptoms = {symptom.lower() for symptom in mapping.get("symptoms", [])}
        return sorted(user_symptoms.intersection(mapped_symptoms))
