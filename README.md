# Prakriti-Aware Recommendation Module (Part 1)

This module provides a structured, explainable, safety-aware recommendation engine for:
- Lifestyle guidance
- Diet guidance
- Home-care guidance

It is designed as a data-driven component in the larger system:
**AI-Based Skin Disease Identification with Ayurvedic Prakriti Personalization**.

## Key Design Principles

- No hardcoded recommendation text inside Python logic
- Knowledge-driven retrieval from JSON files
- Weighted scoring and ranking
- Safety-first gating and filtering
- Explainable output with matched factors and confidence notes
- JSON input/output for easy API integration later

## Project Structure

```text
recommendation_module/
│
├── data/
│   ├── recommendations.json
│   ├── mappings.json
│   └── safety_rules.json
│
├── src/
│   ├── main.py
│   ├── recommendation_engine.py
│   ├── scoring.py
│   ├── safety_filter.py
│   ├── explainability.py
│   ├── data_loader.py
│   └── schemas.py
│
├── tests/
│   └── test_engine.py
│
├── sample_input.json
├── sample_output.json
└── README.md
```

## How It Works

1. **Load and validate input** from `sample_input.json`
2. **Run global safety checks**
   - referral requested
   - low confidence
   - severe condition
3. **Retrieve candidates** by condition + prakriti + symptom overlap
4. **Score candidates** with weighted formula:

   `final_score = (prakriti * 0.30) + (condition * 0.25) + (symptom * 0.20) + (module_conf * 0.10) + (expert * 0.10) + (mapping * 0.05)`

5. **Apply safety filters** (blocked tags, risky recommendations, context conflicts)
6. **Rank and diversify** recommendations across categories where possible
7. **Generate explainable output** with reason and confidence explanation

## Run the Module

From inside `recommendation_module`:

```bash
python3 src/main.py --input sample_input.json --output sample_output.json --top-k 5
```

## Run Tests

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## Visual Interface (Manual Entry Mode)

This module now includes a browser-based UI for manual entry of:
- Prakriti module output
- Skin module output
- User context

### 1) Create and activate a local virtual environment

From workspace root:

```bash
python3 -m venv recommendation_module/.venv
source recommendation_module/.venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r recommendation_module/requirements.txt
```

### 3) Start the web app

```bash
python recommendation_module/src/web_app.py
```

Open [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser.

### 4) Use the interface

- Fill form fields manually (simulating outputs from other modules)
- Click **Generate Recommendations**
- Review grouped results by category (diet, lifestyle, home_care)
- Review confidence level, explanation summary, and referral warning
- Use **Scenario Presets** for one-click demo cases
- Use **Payload JSON** area to import/export full request payloads
- Use **Future Module Integration (Mock)** buttons to simulate upstream module responses

### 5) (Optional) Enable AI-assisted follow-up answers

The Follow-up Assistant chatbot answers most questions with deterministic,
rule-based logic (why-not / compare / what-if), grounded in the engine's own
scored data. For open-ended questions it can't classify (e.g. "what do you
mean by small amount of ghee?"), it can optionally fall back to Claude,
given only the current recommendation text as context — it never invents
facts outside what's already shown to the user.

To enable it, set an API key before starting the server:

```bash
export ANTHROPIC_API_KEY=your-key-here
python recommendation_module/src/web_app.py
```

Without a key set, the assistant works exactly as before (static help
message on unmatched questions) — this feature is fully optional and never
blocks the rest of the app. Answers produced this way are labeled
"AI-assisted" in the chat UI for transparency. Override the model with the
`AI_FALLBACK_MODEL` environment variable if needed (defaults to a small,
fast Claude model).

## Future API Integration

- Replace manual input with calls to the Prakriti and Skin module APIs.
- Keep request/response structure stable (`/api/recommend`) so frontend changes remain minimal.
- Reuse the same UI output rendering logic because engine output is already structured and explainable.

## Notes for Future API Integration

- Keep `sample_input.json` schema as API request contract.
- Replace JSON knowledge files with database tables later.
- Keep scoring/explainability logic unchanged to preserve reproducibility for research.
