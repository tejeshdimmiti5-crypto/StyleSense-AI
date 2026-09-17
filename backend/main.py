from pathlib import Path
import io
import os
import sys

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from ml.infer import predict_image, load_model
except ImportError:
    predict_image = None
    load_model = None

MODEL_PATH = ROOT / "ml" / "artifacts" / "chilli_model.pt"

app = FastAPI(title="ChilliProfit AI API", version="0.4.0", description="Backend API for chilli leaf screening and farm intelligence.")

frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")
app.add_middleware(CORSMiddleware, allow_origins=[frontend_origin] if frontend_origin != "*" else ["*"], allow_credentials=frontend_origin != "*", allow_methods=["*"], allow_headers=["*"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = 10 * 1024 * 1024


def model_available():
    return MODEL_PATH.exists() and predict_image is not None


def model_metadata():
    if not model_available() or load_model is None:
        return None
    try:
        loaded = load_model(str(MODEL_PATH))
        if loaded is None:
            return None
        _, class_names = loaded
        return {"architecture": "EfficientNet-B0", "classes": class_names, "image_size": 224}
    except Exception:
        return None


@app.get("/")
def root():
    return {"service": "ChilliProfit AI", "status": "online"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "ChilliProfit AI"}


@app.get("/api/health")
def api_health():
    return {"status": "ok", "model_configured": model_available(), "model_path": str(MODEL_PATH), "model": model_metadata()}


@app.post("/api/analyze")
async def analyze_leaf(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Upload a JPG, PNG or WEBP image.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image must be 10 MB or smaller.")

    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid image.") from exc

    if not model_available():
        return {"status": "model_not_configured", "title": "Image ready for AI screening", "message": "The image was validated successfully. Train the model to enable disease prediction.", "confidence": None, "severity": "Pending model", "zone": "Not assigned", "next_step": "Train the chilli model", "filename": Path(file.filename or "leaf").name, "image_size": {"width": image.width, "height": image.height}}

    try:
        result = predict_image(image, MODEL_PATH)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {exc}") from exc

    if result is None:
        raise HTTPException(status_code=503, detail="The trained model is unavailable.")

    disease = result["class_name"]
    confidence = result["confidence"]
    is_healthy = disease.strip().lower() == "healthy"
    screening_band = "High confidence" if confidence >= 85 else "Moderate confidence" if confidence >= 60 else "Low confidence"
    next_step = "Continue monitoring and rescan if symptoms change" if is_healthy else "Inspect nearby plants and confirm the result with an agricultural professional"

    return {"status": "prediction", "title": disease.replace("_", " ").title(), "message": "Model prediction generated from the uploaded chilli leaf image.", "confidence": confidence, "severity": screening_band, "zone": "Not assigned", "next_step": next_step, "probabilities": result["probabilities"], "filename": Path(file.filename or "leaf").name, "image_size": {"width": image.width, "height": image.height}}
