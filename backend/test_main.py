import io

from fastapi.testclient import TestClient
from PIL import Image

from backend.main import MODEL_SHA256, MODEL_VERSION, app

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
    if body["model_configured"]:
        assert body["model"]["version"] == MODEL_VERSION
        assert body["model"]["sha256"] == MODEL_SHA256
        assert body["model"]["architecture"] == "EfficientNet-B0"
        assert len(body["model"]["classes"]) == 5


def test_rejects_non_image():
    response = client.post(
        "/api/analyze",
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 415


def test_accepts_valid_image_and_preserves_zone():
    response = client.post(
        "/api/analyze",
        files={"file": ("leaf.png", make_png(), "image/png")},
        data={"zone": "Zone 4"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"model_not_configured", "prediction"}
    assert body["filename"] == "leaf.png"
    assert body["image_size"] == {"width": 32, "height": 32}
    assert body["zone"] == "Zone 4"
    if body["status"] == "prediction":
        assert body["model"]["version"] == MODEL_VERSION
        assert body["model"]["sha256"] == MODEL_SHA256


def test_empty_zone_defaults_to_not_assigned():
    response = client.post(
        "/api/analyze",
        files={"file": ("leaf.png", make_png(), "image/png")},
        data={"zone": "   "},
    )
    assert response.status_code == 200
    assert response.json()["zone"] == "Not assigned"


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
