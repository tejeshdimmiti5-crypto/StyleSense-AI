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

app = FastAPI(
    title="ChilliProfit AI API",
    version="0.2.0",
    description="Backend API for chilli leaf screening and farm intelligence.",
)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin] if frontend_origin != "*" else ["*"],
    allow_credentials=frontend_origin != "*",
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = 10 * 1024 * 1024


def model_available():
    return MODEL_PATH.exists() and predict_image is not None


@app.get("/")
def root():
    return {"service": "ChilliProfit AI", "status": "online"}


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "model_configured": model_available(),
        "model_path": str(MODEL_PATH),
    }


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
        return {
            "status": "model_not_configured",
            "title": "Image ready for AI screening",
            "message": "The image was validated successfully. Train the model locally to enable disease prediction.",
            "confidence": None,
            "severity": "Pending model",
            "zone": "Not assigned",
            "next_step": "Train the chilli model",
            "filename": Path(file.filename or "leaf").name,
            "image_size": {"width": image.width, "height": image.height},
        }

    try:
        result = predict_image(image, MODEL_PATH)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {exc}") from exc

    if result is None:
        raise HTTPException(status_code=503, detail="The trained model is unavailable.")

    disease = result["class_name"]
    confidence = result["confidence"]
    severity_value = "High" if confidence >= 85 and disease != "healthy" else "Moderate" if disease != "healthy" else "Low"
    next_step = "Continue monitoring" if disease == "healthy" else "Inspect nearby plants and confirm with an agricultural professional"

    return {
        "status": "prediction",
        "title": disease.replace("_", " ").title(),
        "message": "Model prediction generated from the uploaded chilli leaf image.",
        "confidence": confidence,
        "severity": severity_value,
        "zone": "Not assigned",
        "next_step": next_step,
        "probabilities": result["probabilities"],
        "filename": Path(file.filename or "leaf").name,
        "image_size": {"width": image.width, "height": image.height},
    }
