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
- `GET /api/health` — health/model status
- `POST /api/analyze` — validates and screens an uploaded chilli leaf image

The API does not return a fabricated disease result. With the trained checkpoint available, `/api/analyze` runs the EfficientNet-B0 classifier and returns the predicted class, confidence and probability distribution.

## Trained model

The first model was successfully trained by GitHub Actions run `35230162129` and published as release `model-1`.

- Architecture: EfficientNet-B0
- Classes: `cercospora`, `healthy`, `mites_and_trips`, `nutritional`, `powdery mildew`
- Test accuracy: 88.75%
- Test macro F1: 0.8798
- Checkpoint size: about 16.4 MB

Model release asset:

`https://github.com/tejeshdimmiti5-crypto/StyleSense-AI/releases/download/model-1/chilli_model.pt`

SHA-256:

`b2db895fd43bf801fcc522c3f749fe8f5a9766583cc0e4f336a3553e645bb0ce`

## Production model bootstrap

`backend.fetch_model` can download the checkpoint when the API starts. Set these environment variables on the deployment platform:

```text
CHILLIPROFIT_MODEL_URL=https://github.com/tejeshdimmiti5-crypto/StyleSense-AI/releases/download/model-1/chilli_model.pt
CHILLIPROFIT_MODEL_SHA256=b2db895fd43bf801fcc522c3f749fe8f5a9766583cc0e4f336a3553e645bb0ce
```

The SHA-256 value is optional but recommended so the downloaded model is verified before use.

## Dataset

The primary training source is the raw COLD chilli-leaf dataset from Hugging Face. The training pipeline keeps the downloaded images outside GitHub and uses a stratified train/validation/test split with training-only augmentation.

The Krishna River Basin dataset remains an external validation source and is not silently mixed into training.

## Important

The model is a research screening prototype, not a definitive agricultural diagnosis. Test-set metrics do not guarantee field performance. Field images should be used for additional validation before relying on predictions for treatment decisions.
