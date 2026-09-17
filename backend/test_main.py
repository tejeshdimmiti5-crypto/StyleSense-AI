import io

from fastapi.testclient import TestClient
from PIL import Image

from backend.main import app

client = TestClient(app)


def make_image_bytes():
    image = Image.new("RGB", (32, 32), (80, 140, 60))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "ChilliProfit AI"


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "model_configured" in response.json()


def test_rejects_non_image_upload():
    response = client.post(
        "/api/analyze",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 415


def test_accepts_valid_image_without_fake_prediction():
    response = client.post(
        "/api/analyze",
        files={"file": ("leaf.png", make_image_bytes(), "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"model_not_configured", "prediction"}
    assert body["filename"] == "leaf.png"
