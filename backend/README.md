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
- `GET /api/health` — health/model status
- `POST /api/analyze` — validates an uploaded chilli leaf image

The current `/api/analyze` endpoint deliberately does **not** return a fake disease classification. It returns `model_not_configured` until a trained computer-vision model is connected.

## Dataset plan

The first training source will be public chilli-leaf datasets. The COLD chilli dataset contains 10,987 processed images across five classes: Healthy, Cercospora, Mites and Trips, Nutritional Deficiency, and Powdery Mildew. Its raw collection contains 532 original photographs; the larger set includes augmentation. The dataset is publicly available under CC BY 4.0. See the project paper and dataset sources before redistribution. 

A second useful source is the 2026 Krishna River Basin chilli dataset, which includes field images from Andhra Pradesh districts including Guntur and Prakasam, plus Karnataka locations. It contains healthy/diseased chilli leaves and growth-stage images. 

We will keep downloaded datasets outside this GitHub repository and train from a local `data/` directory to avoid committing large image files.

## Next ML stage

1. Download approved public datasets.
2. Inspect class names and licenses.
3. Remove corrupted/duplicate images.
4. Create train/validation/test splits without leakage.
5. Train a transfer-learning classifier.
6. Evaluate accuracy, precision, recall, F1 and confusion matrix.
7. Export the best model.
8. Connect inference to `/api/analyze`.
