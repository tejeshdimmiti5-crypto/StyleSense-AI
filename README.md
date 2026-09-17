# 🌶️ ChilliProfit AI

**AI-Based Chilli Disease Detection and Farm Intelligence Platform**

ChilliProfit AI is a smart-farming platform designed to help chilli growers monitor crop health, identify possible diseases from leaf images, understand farm-zone risk and evaluate farm economics.

The platform is **not limited to a fixed farm size**. Farm zones, crop observations and economic inputs are designed to scale according to the user's actual farm.

## Current architecture

```text
Leaf Image
   ↓
FastAPI validation
   ↓
EfficientNet-B0 chilli classifier
   ↓
Disease class + confidence + probability distribution
   ↓
Farm-zone interface
   ↓
Risk / yield / economics features
```

The repository includes the FastAPI inference API, reproducible PyTorch training pipeline, model inference module, automated GitHub Actions training workflow, model integrity manifest generation, and release publishing. The production API can bootstrap a trained model from a GitHub release using environment variables.

## Current application

- Chilli-focused responsive web interface
- Leaf image upload and preview
- Backend-connected disease screening workflow
- Scalable farm-zone health map
- Zone risk indicators
- Revenue and net-return calculator
- FastAPI health and model-status endpoints
- Image validation and upload-size protection
- EfficientNet-B0 transfer-learning classifier
- Confidence and probability reporting
- Automated model artifact and SHA-256 publishing

> **Important:** A model prediction is a screening aid, not a definitive agricultural diagnosis. The API deliberately avoids presenting confidence as biological disease severity. Field confirmation and qualified agricultural guidance are appropriate before treatment decisions.

## Machine-learning pipeline

Primary training dataset:

`Project-AgML/COLD_chili_leaf_disease_classification`

Training uses the raw image collection, a stratified train/validation/test split, training-only augmentation, class-weighted loss, EfficientNet-B0 transfer learning, early stopping and macro-F1 model selection. The training workflow produces:

- `chilli_model.pt` — trained checkpoint
- `chilli_model.json` — evaluation metrics and confusion matrix
- `chilli_model.sha256` — integrity manifest

The Krishna River Basin chilli dataset is kept as an external validation source and is not silently mixed into training.

## Technology stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python + FastAPI
- ML: PyTorch + torchvision
- Model: EfficientNet-B0 transfer learning
- Data: Hugging Face datasets + external field validation dataset
- Deployment: Docker + Render configuration
- Model delivery: GitHub Releases

API keys and secrets should **never** be committed to this repository. Use environment variables on the backend.

## Backend endpoints

- `GET /` — service status
- `GET /health` — deployment health check
- `GET /api/health` — API and model status
- `POST /api/analyze` — validate and screen a chilli leaf image

## Model bootstrap

The Docker image runs `backend.fetch_model` before starting FastAPI. Configure `CHILLIPROFIT_MODEL_URL` with the trained release asset URL and optionally set `CHILLIPROFIT_MODEL_SHA256` to verify the downloaded checkpoint.

## Roadmap

- [x] Build responsive chilli-farming interface
- [x] Add FastAPI image-analysis endpoint
- [x] Add reproducible transfer-learning training pipeline
- [x] Add model inference integration
- [x] Add automated model training and release workflow
- [x] Add Docker and Render deployment configuration
- [ ] Complete first successful trained-model release
- [ ] Validate shared classes on Krishna Basin field images
- [ ] Add disease severity estimation as a separate calibrated model
- [ ] Replace demo farm zones with user-defined farm layouts
- [ ] Add weather and soil inputs
- [ ] Add yield prediction
- [ ] Add richer cost/profit scenarios
- [ ] Add Telugu + English farmer interface
- [ ] Deploy and verify production API

## Project name

**ChilliProfit AI — Smart Chilli Farming Intelligence**
