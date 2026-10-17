# Recommendation Module Run Guide

## 1) Prerequisites

- Python 3.10+ installed
- Project folder available locally:
  - `recommendation_module/`

## 2) Project Structure (Relevant for Running)

- `src/main.py` -> CLI runner
- `src/web_app.py` -> web interface server
- `sample_input.json` -> sample request payload
- `sample_output.json` -> generated sample output
- `requirements.txt` -> Python dependencies
- `tests/` -> test suite

## 3) Setup Virtual Environment

From workspace root:

```bash
python3 -m venv recommendation_module/.venv
source recommendation_module/.venv/bin/activate
pip install -r recommendation_module/requirements.txt
```

## 4) Run in CLI Mode

Use this when you want JSON-in / JSON-out execution.

```bash
python recommendation_module/src/main.py \
  --input recommendation_module/sample_input.json \
  --output recommendation_module/sample_output.json \
  --top-k 6
```

Expected terminal output:
- Output file path
- Status (`success` or `referral_recommended`)
- Number of recommendations returned

## 5) Run in Web Interface Mode

Use this when you want visual/manual input and grouped recommendation display.

```bash
python recommendation_module/src/web_app.py
```

Open in browser:
- [http://127.0.0.1:5001](http://127.0.0.1:5001)

What you can do in UI:
- Enter Prakriti + Skin + User context manually
- Use scenario preset buttons
- Generate recommendations
- View grouped output (`diet`, `lifestyle`, `home_care`)
- Export payload/output JSON

## 6) Run Tests

From workspace root:

```bash
recommendation_module/.venv/bin/python -m unittest discover -s recommendation_module/tests -p "test_*.py"
```

Or after activating venv:

```bash
python -m unittest discover -s recommendation_module/tests -p "test_*.py"
```

## 7) Quick API Check (Optional)

When web app is running, test health endpoint:

```bash
curl http://127.0.0.1:5001/api/health
```

Expected response:

```json
{"status":"ok"}
```

## 8) Common Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'flask'`
Fix:
- Activate venv and install requirements again:

```bash
source recommendation_module/.venv/bin/activate
pip install -r recommendation_module/requirements.txt
```

### Issue: Port already in use (`5001`)
Fix:
- Stop previous process (Ctrl+C in old terminal), or change port in `src/web_app.py`.

### Issue: No recommendations returned
Possible reasons:
- Referral required
- Severe case safety gating
- Very low confidence
- Symptom/condition mismatch with mappings

Check:
- Input payload values
- `data/mappings.json` and safety rules

## 9) Recommended Demo Flow

1. Start web app
2. Load sample or preset scenario
3. Click **Generate Recommendations**
4. Show grouped explainable output
5. Mention future integration path:
   - Replace manual input with Prakriti/Skin module API outputs
