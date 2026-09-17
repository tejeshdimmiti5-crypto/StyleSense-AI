# ChilliProfit AI Backend

FastAPI backend for the ChilliProfit AI web application.

## Local setup

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API will run at `http://127.0.0.1:8000`.

## Endpoints

- `GET /` — service status
- `GET /health` — deployment health check
- `GET /api/health` — API and trained-model status
- `POST /api/analyze` — validates and screens an uploaded chilli leaf image

## Trained model

The first trained ChilliProfit model is published as GitHub Release `model-1` and uses EfficientNet-B0 transfer learning with five classes:

- `cercospora`
- `healthy`
- `mites_and_trips`
- `nutritional`
- `powdery_mildew`

The model is loaded automatically when `ml/artifacts/chilli_model.pt` exists. For Docker/Render deployment, `backend.fetch_model` downloads the release asset when `CHILLIPROFIT_MODEL_URL` is configured and verifies it when `CHILLIPROFIT_MODEL_SHA256` is set.

Model-1 held-out COLD test results are 88.75% accuracy and 0.8798 macro F1. These are dataset test results, not field-accuracy claims.

## Environment variables

```text
FRONTEND_ORIGIN=https://your-frontend.example
CHILLIPROFIT_MODEL_URL=https://github.com/tejeshdimmiti5-crypto/StyleSense-AI/releases/download/model-1/chilli_model.pt
CHILLIPROFIT_MODEL_SHA256=b2db895fd43bf801fcc522c3f749fe8f5a9766583cc0e4f336a3553e645bb0ce
CHILLIPROFIT_MODEL_VERSION=model-1
```

`CHILLIPROFIT_MODEL_VERSION` identifies the model release reported by `/api/health` and `/api/analyze`. It defaults to `model-1` when omitted.

The model URL and SHA above are public release metadata; API keys and other secrets must never be committed.

## API behavior

`POST /api/analyze` validates JPEG, PNG and WEBP uploads and rejects empty, invalid or oversized files. With the trained model available it returns the predicted class, model confidence, class probabilities and a recommended next step.

The optional multipart form field `zone` identifies the farm-map zone associated with the uploaded leaf. If it is omitted or blank, the API returns `Not assigned`. The current frontend keeps farm-map zone state in the browser; the API does not persist zone state between sessions.

The returned confidence is a model-screening confidence measure, **not biological disease severity**. The application should not use it as a substitute for field diagnosis or qualified agricultural guidance.

## Production verification

After the API is deployed, run the GitHub Actions workflow **Production API verification** manually and provide the deployed API base URL. The workflow checks `/health`, `/api/health`, confirms the EfficientNet-B0 model is configured, validates the expected model version and SHA256, and sends a real JPEG through `/api/analyze` with a selected zone to verify end-to-end inference.

## Testing

From the repository root:

```bash
pytest backend/test_main.py
```
