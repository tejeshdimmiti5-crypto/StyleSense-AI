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
```

The model URL and SHA above are public release metadata; API keys and other secrets must never be committed.

## API behavior

`POST /api/analyze` validates JPEG, PNG and WEBP uploads and rejects empty, invalid or oversized files. With the trained model available it returns the predicted class, model confidence, class probabilities and a recommended next step.

The returned confidence is a model-screening confidence measure, **not biological disease severity**. The application should not use it as a substitute for field diagnosis or qualified agricultural guidance.

## Production verification

After the API is deployed, run the GitHub Actions workflow **Production API verification** manually and provide the deployed API base URL. The workflow checks `/health`, `/api/health`, confirms the EfficientNet-B0 model is configured, and sends a real JPEG through `/api/analyze` to verify end-to-end inference.

## Testing

From the repository root:

```bash
pytest backend/test_main.py
```
