"""Evaluate a trained COLD model on shared classes from the Krishna Basin set."""

import argparse
import json
from pathlib import Path
import sys

import torch
from PIL import Image
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from torchvision import transforms

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
SHARED_CLASSES = ["healthy", "cercospora", "nutritional"]
TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="ml/data/krishna_basin")
    parser.add_argument("--model", default="ml/artifacts/chilli_model.pt")
    parser.add_argument("--output", default="ml/artifacts/external_validation.json")
    args = parser.parse_args()

    loaded = load_model(args.model)
    if loaded is None:
        raise SystemExit("Model checkpoint not found. Train the model first.")
    model, class_names = loaded

    root = Path(args.data)
    if not root.exists():
        raise SystemExit(f"External dataset directory not found: {root}")

    true, pred = [], []
    skipped = 0
    discovered = 0

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
            discovered += 1
            try:
                image = Image.open(path).convert("RGB")
            except Exception:
                skipped += 1
                continue
            with torch.inference_mode():
                output = model(TRANSFORM(image).unsqueeze(0))
            pred_id = int(output.argmax(1).item())
            true.append(target_id)
            pred.append(pred_id)

    if not true:
        raise SystemExit("No matching external images found.")

    labels = [class_names.index(name) for name in SHARED_CLASSES if name in class_names]
    names = [class_names[i] for i in labels]
    report = classification_report(
        true, pred, labels=labels, target_names=names, zero_division=0, output_dict=True
    )
    matrix = confusion_matrix(true, pred, labels=labels).tolist()

    metrics = {
        "model": str(args.model),
        "dataset": str(root),
        "shared_classes": names,
        "images_discovered": discovered,
        "images_evaluated": len(true),
        "images_skipped": skipped,
        "accuracy": float(accuracy_score(true, pred)),
        "macro_f1": float(f1_score(true, pred, labels=labels, average="macro", zero_division=0)),
        "per_class": {
            name: {
                "precision": float(report[name]["precision"]),
                "recall": float(report[name]["recall"]),
                "f1": float(report[name]["f1-score"]),
                "support": int(report[name]["support"]),
            }
            for name in names
        },
        "confusion_matrix": matrix,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metrics, indent=2))

    print(classification_report(true, pred, labels=labels, target_names=names, zero_division=0))
    print("Confusion matrix:")
    print(matrix)
    print(f"Evaluated images: {len(true)} | skipped: {skipped}")
    print(f"Saved report: {output}")


if __name__ == "__main__":
    main()
