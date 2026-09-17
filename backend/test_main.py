import io

from fastapi.testclient import TestClient
from PIL import Image

from backend.main import app

client = TestClient(app)


def make_png():
    image = Image.new("RGB", (32, 32), (40, 140, 60))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "ChilliProfit AI"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "model_configured" in body
    assert "model" in body


def test_rejects_non_image():
    response = client.post(
        "/api/analyze",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 415


def test_accepts_valid_image():
    response = client.post(
        "/api/analyze",
        files={"file": ("leaf.png", make_png(), "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"model_not_configured", "prediction"}
    assert "filename" in body
    assert body["filename"] == "leaf.png"
    assert "image_size" in body


def test_rejects_empty_image():
    response = client.post(
        "/api/analyze",
        files={"file": ("empty.png", b"", "image/png")},
    )
    assert response.status_code == 400


def test_rejects_invalid_image_bytes():
    response = client.post(
        "/api/analyze",
        files={"file": ("fake.png", b"not really png", "image/png")},
    )
    assert response.status_code == 400
