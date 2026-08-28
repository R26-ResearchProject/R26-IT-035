"""Basic tests for recommendation engine behavior."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from data_loader import load_json, load_knowledge_base, validate_input
from recommendation_engine import RecommendationEngine


class RecommendationEngineTests(unittest.TestCase):
    """Unit tests for core recommendation flow."""

    def setUp(self) -> None:
        self.knowledge = load_knowledge_base(ROOT / "data")
        self.engine = RecommendationEngine(self.knowledge)
        self.user_input = load_json(ROOT / "sample_input.json")
        validate_input(self.user_input)

    def _total(self, output: dict) -> int:
        grouped = output.get("recommendations_by_category", {})
        return sum(len(items) for items in grouped.values())

    def test_vata_eczema_dryness_case(self) -> None:
        case_input = dict(self.user_input)
        case_input["skin_result"] = dict(self.user_input["skin_result"])
        case_input["skin_result"]["predicted_condition"] = "Eczema"
        case_input["skin_result"]["symptoms"] = ["dryness", "itching"]
        output = self.engine.generate(case_input, top_k=5)
        self.assertEqual(output["status"], "success")
        self.assertGreater(self._total(output), 0)

    def test_pitta_acne_redness_case(self) -> None:
        case_input = dict(self.user_input)
        case_input["prakriti_result"] = dict(self.user_input["prakriti_result"])
        case_input["skin_result"] = dict(self.user_input["skin_result"])
        case_input["prakriti_result"]["dominant_prakriti"] = "Pitta"
        case_input["prakriti_result"]["secondary_prakriti"] = "Vata"
        case_input["prakriti_result"]["prakriti_scores"] = {"vata": 0.2, "pitta": 0.7, "kapha": 0.1}
        case_input["skin_result"]["predicted_condition"] = "Acne"
        case_input["skin_result"]["symptoms"] = ["redness", "oiliness", "inflammation"]
        output = self.engine.generate(case_input, top_k=5)
        self.assertEqual(output["status"], "success")
        self.assertGreater(self._total(output), 0)
        self.assertIn(output["overall_confidence_level"], {"high", "medium", "low"})

    def test_kapha_fungal_infection_case(self) -> None:
        case_input = dict(self.user_input)
        case_input["prakriti_result"] = dict(self.user_input["prakriti_result"])
        case_input["skin_result"] = dict(self.user_input["skin_result"])
        case_input["prakriti_result"]["dominant_prakriti"] = "Kapha"
        case_input["prakriti_result"]["secondary_prakriti"] = "Pitta"
        case_input["prakriti_result"]["prakriti_scores"] = {"vata": 0.05, "pitta": 0.25, "kapha": 0.7}
        case_input["skin_result"]["predicted_condition"] = "Fungal Infection"
        case_input["skin_result"]["symptoms"] = ["itching", "moist_patches", "sweating"]
        output = self.engine.generate(case_input, top_k=5)
        self.assertEqual(output["status"], "success")
        self.assertGreater(self._total(output), 0)

    def test_low_confidence_case(self) -> None:
        case_input = dict(self.user_input)
        case_input["prakriti_result"] = dict(self.user_input["prakriti_result"])
        case_input["skin_result"] = dict(self.user_input["skin_result"])
        case_input["prakriti_result"]["confidence"] = 0.4
        case_input["skin_result"]["confidence"] = 0.55
        output = self.engine.generate(case_input, top_k=5)
        self.assertEqual(output["status"], "referral_recommended")
        self.assertEqual(self._total(output), 0)

    def test_severe_condition_case(self) -> None:
        case_input = dict(self.user_input)
        case_input["skin_result"] = dict(self.user_input["skin_result"])
        case_input["skin_result"]["severity"] = "severe"
        output = self.engine.generate(case_input, top_k=5)
        self.assertEqual(output["status"], "referral_recommended")
        self.assertEqual(self._total(output), 0)


if __name__ == "__main__":
    unittest.main()
