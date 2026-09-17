"""Evaluate the trained COLD model on shared classes from the Krishna Basin set.

Expected directory layout:
ml/data/krishna_basin/
  Healthy Leaves/*.jpg
  Cercospora Leaf Spot/*.jpg
  Nutrition Deficiency/*.jpg
  ...other classes are ignored because the COLD model has no matching labels.

Only semantically shared classes are evaluated:
healthy -> healthy
cercospora leaf spot -> cercospora
nutrition deficiency -> nutritional
"""

import argparse
from pathlib import Path

import torch
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix
from torchvision import transforms

from infer import load_model

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
LABEL_MAP = {
    "healthy leaves": "healthy",
    "healthy": "healthy",
    "cercospora leaf spot": "cercospora",
    "cercospora": "cercospora",
    "nutrition deficiency": "nutritional",
    "nutritional": "nutritional",
}
TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="ml/data/krishna_basin")
    parser.add_argument("--model", default="ml/artifacts/chilli_model.pt")
    args = parser.parse_args()

    loaded = load_model(args.model)
    if loaded is None:
        raise SystemExit("Model checkpoint not found. Train the model first.")
    model, class_names = loaded

    root = Path(args.data)
    true, pred = [], []
    for folder in root.iterdir():
        if not folder.is_dir():
            continue
        target = LABEL_MAP.get(folder.name.strip().lower())
        if target not in class_names:
            continue
        target_id = class_names.index(target)
        for path in folder.rglob("*"):
            if path.suffix.lower() not in IMAGE_EXTS:
                continue
            try:
                image = Image.open(path).convert("RGB")
            except Exception:
                continue
            with torch.no_grad():
                output = model(TRANSFORM(image).unsqueeze(0))
            pred_id = int(output.argmax(1).item())
            true.append(target_id)
            pred.append(pred_id)

    if not true:
        raise SystemExit("No matching external images found.")

    labels = [class_names.index(name) for name in ["healthy", "cercospora", "nutritional"] if name in class_names]
    names = [class_names[i] for i in labels]
    print(classification_report(true, pred, labels=labels, target_names=names, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(true, pred, labels=labels))
    print(f"Evaluated images: {len(true)}")


if __name__ == "__main__":
    main()
