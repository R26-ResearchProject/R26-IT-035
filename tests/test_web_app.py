"""Basic API tests for the Flask visual interface backend."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from data_loader import load_json
from web_app import app


class WebAppTests(unittest.TestCase):
    """Verify web endpoints used by UI."""

    def setUp(self) -> None:
        app.testing = True
        self.client = app.test_client()
        self.sample_input = load_json(ROOT / "sample_input.json")

    def test_health_endpoint(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_recommend_endpoint_success(self) -> None:
        response = self.client.post("/api/recommend", json=self.sample_input)
        self.assertEqual(response.status_code, 200)
        self.assertIn("recommendations_by_category", response.json)

    def test_module_sim_endpoint_prakriti(self) -> None:
        response = self.client.get("/api/module-sim/prakriti")
        self.assertEqual(response.status_code, 200)
        self.assertIn("dominant_prakriti", response.json["data"])


if __name__ == "__main__":
    unittest.main()
