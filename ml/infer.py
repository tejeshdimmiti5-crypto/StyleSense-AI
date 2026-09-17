"""Load the trained ChilliProfit classifier and run one-image inference."""

from functools import lru_cache
from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torchvision import models, transforms

DEFAULT_MODEL = Path(__file__).parent / "artifacts" / "chilli_model.pt"

TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


@lru_cache(maxsize=2)
def load_model(model_path_str: str = str(DEFAULT_MODEL)):
    """Load a checkpoint once and reuse it for subsequent API requests."""
    model_path = Path(model_path_str)
    if not model_path.exists():
        return None

    checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
    class_names = checkpoint["class_names"]
    model = models.efficientnet_b0(weights=None)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(class_names))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model, class_names


def predict_image(image: Image.Image, model_path=DEFAULT_MODEL):
    """Return class probabilities for one RGB image."""
    loaded = load_model(str(Path(model_path)))
    if loaded is None:
        return None

    model, class_names = loaded
    tensor = TRANSFORM(image.convert("RGB")).unsqueeze(0)
    with torch.inference_mode():
        probabilities = torch.softmax(model(tensor), dim=1)[0]
        confidence, index = probabilities.max(dim=0)

    return {
        "class_name": class_names[index.item()],
        "confidence": round(float(confidence) * 100, 2),
        "probabilities": {
            name: round(float(probabilities[i]) * 100, 2)
            for i, name in enumerate(class_names)
        },
    }
