from pathlib import Path
import io
import os

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

app = FastAPI(
    title="ChilliProfit AI API",
    version="0.1.0",
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


@app.get("/")
def root():
    return {"service": "ChilliProfit AI", "status": "online"}


@app.get("/api/health")
def health():
    return {"status": "ok", "model_configured": False}


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
        image = Image.open(io.BytesIO(data))
        image.verify()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid image.") from exc

    # This endpoint intentionally does not invent a disease prediction.
    # Replace this section with the trained classifier once the dataset/model is ready.
    return {
        "status": "model_not_configured",
        "title": "Image ready for AI screening",
        "message": "The image was validated successfully. Train and connect the chilli disease model to produce a real prediction.",
        "confidence": None,
        "severity": "Pending model",
        "zone": "Not assigned",
        "next_step": "Connect the trained model",
        "filename": Path(file.filename or "leaf").name,
        "image_size": {"width": image.width, "height": image.height},
    }
