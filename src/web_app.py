"""Flask web app for manual recommendation module testing."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request

from data_loader import load_json, load_knowledge_base, validate_input
from followup_qa import answer_question
from recommendation_engine import RecommendationEngine
from report_generator import build_report_pdf

# Resolve project directories once so both CLI and UI stay in sync.
BASE_DIR = Path(__file__).resolve().parent.parent
UI_DIR = BASE_DIR / "ui"
DATA_DIR = BASE_DIR / "data"
SAMPLE_INPUT_PATH = BASE_DIR / "sample_input.json"

# Loads ANTHROPIC_API_KEY (and any other config) from recommendation_module/.env
# if present. A real process env var always takes precedence over the .env file.
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__, template_folder=str(UI_DIR / "templates"), static_folder=str(UI_DIR / "static"))
engine = RecommendationEngine(load_knowledge_base(DATA_DIR))


@app.get("/")
def index() -> str:
    """Render the single-page UI with default sample values."""
    sample_input = load_json(SAMPLE_INPUT_PATH)
    return render_template("index.html", sample_input=sample_input)


@app.get("/api/health")
def health() -> Dict[str, str]:
    """Basic health endpoint for integration checks."""
    return {"status": "ok"}


@app.get("/api/sample-input")
def sample_input() -> Dict[str, Any]:
    """Return sample payload for quick UI reset/fill."""
    return load_json(SAMPLE_INPUT_PATH)


@app.post("/api/recommend")
def recommend() -> Any:
    """Validate request JSON, run engine, and return structured response."""
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"status": "error", "message": "Invalid or missing JSON payload."}), 400

    try:
        validate_input(payload)
        top_k = int(request.args.get("top_k", 6))
        result = engine.generate(payload, top_k=top_k)
        return jsonify(result)
    except ValueError as error:
        return jsonify({"status": "error", "message": str(error)}), 400
    except Exception as error:  # noqa: BLE001
        return jsonify({"status": "error", "message": f"Internal error: {error}"}), 500


@app.post("/api/report/pdf")
def report_pdf() -> Any:
    """Generate a downloadable PDF report for the given profile payload."""
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"status": "error", "message": "Invalid or missing JSON payload."}), 400

    try:
        validate_input(payload)
        top_k = int(request.args.get("top_k", 6))
        result = engine.generate(payload, top_k=top_k)
        pdf_bytes = build_report_pdf(payload, result)
        filename = f"recommendation_report_{result.get('user_id', 'user')}.pdf"
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as error:
        return jsonify({"status": "error", "message": str(error)}), 400
    except Exception as error:  # noqa: BLE001
        return jsonify({"status": "error", "message": f"Internal error: {error}"}), 500


@app.post("/api/followup")
def followup() -> Any:
    """Answer a follow-up question about the last recommendation run.

    Stateless by design (matches /api/recommend): the client resends the
    profile payload it last submitted, and this re-derives the full scored
    candidate pool + exclusion reasons needed to answer accurately.
    """
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"status": "error", "message": "Invalid or missing JSON payload."}), 400

    question = body.get("question", "")
    payload = body.get("payload")
    top_k = int(body.get("top_k", 6))

    if not payload:
        return jsonify({"status": "error", "message": "Missing 'payload' (the last recommendation request)."}), 400

    try:
        validate_input(payload)
        analysis = engine.analyze(payload, top_k=top_k)
        response = answer_question(question, payload, analysis, engine, top_k=top_k)
        return jsonify({"status": "success", **response})
    except ValueError as error:
        return jsonify({"status": "error", "message": str(error)}), 400
    except Exception as error:  # noqa: BLE001
        return jsonify({"status": "error", "message": f"Internal error: {error}"}), 500


@app.get("/api/module-sim/<module_name>")
def module_sim(module_name: str) -> Any:
    """Return mock upstream module outputs for staged integration demos."""
    sample_payload = load_json(SAMPLE_INPUT_PATH)
    if module_name == "prakriti":
        return jsonify({"module": "prakriti", "data": sample_payload["prakriti_result"]})
    if module_name == "skin":
        return jsonify({"module": "skin", "data": sample_payload["skin_result"]})
    return jsonify({"status": "error", "message": f"Unknown module: {module_name}"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5001)
