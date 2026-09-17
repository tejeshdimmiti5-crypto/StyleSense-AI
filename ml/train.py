"""Train a chilli-leaf disease classifier.

Default dataset: raw COLD chilli dataset from Hugging Face.
The script deliberately uses the raw subset rather than the augmented subset
so that augmentation is generated only inside the training split and does not
leak augmented copies into validation/test data.
"""

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from datasets import load_dataset
from PIL import Image
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from tqdm import tqdm

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


class LeafDataset(Dataset):
    def __init__(self, rows, labels, transform):
        self.rows = rows
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        image = self.rows[idx]["image"]
        if not isinstance(image, Image.Image):
            image = Image.open(image)
        image = image.convert("RGB")
        return self.transform(image), self.labels[idx]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="Project-AgML/COLD_chili_leaf_disease_classification")
    parser.add_argument("--config", default="raw", help="HF dataset config/subset")
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--output", default="ml/artifacts/chilli_model.pt")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    ds = load_dataset(args.dataset, args.config, split="train")
    label_feature = ds.features["label"]
    class_names = label_feature.names
    labels = list(ds["label"])

    # Stratified 70/15/15 split from the original images.
    train_idx, temp_idx = train_test_split(
        np.arange(len(ds)), test_size=0.30, random_state=SEED, stratify=labels
    )
    temp_labels = [labels[i] for i in temp_idx]
    val_idx, test_idx = train_test_split(
        temp_idx, test_size=0.50, random_state=SEED, stratify=temp_labels
    )

    train_tfms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(12),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.10),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    eval_tfms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    train_rows = ds.select(train_idx.tolist())
    val_rows = ds.select(val_idx.tolist())
    test_rows = ds.select(test_idx.tolist())
    train_labels = [labels[i] for i in train_idx]
    val_labels = [labels[i] for i in val_idx]
    test_labels = [labels[i] for i in test_idx]

    train_loader = DataLoader(LeafDataset(train_rows, train_labels, train_tfms), batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(LeafDataset(val_rows, val_labels, eval_tfms), batch_size=args.batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(LeafDataset(test_rows, test_labels, eval_tfms), batch_size=args.batch_size, shuffle=False, num_workers=0)

    model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(class_names))
    model.to(device)

    # Class-weighted loss helps when the source dataset is imbalanced.
    counts = np.bincount(train_labels, minlength=len(class_names))
    weights = len(train_labels) / (len(class_names) * np.maximum(counts, 1))
    criterion = nn.CrossEntropyLoss(weight=torch.tensor(weights, dtype=torch.float32, device=device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)

    best_f1 = -1.0
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(args.epochs):
        model.train()
        running_loss = 0.0
        for x, y in tqdm(train_loader, desc=f"Epoch {epoch + 1}/{args.epochs}"):
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * x.size(0)

        val_true, val_pred = predict(model, val_loader, device)
        val_acc = accuracy_score(val_true, val_pred)
        val_f1 = f1_score(val_true, val_pred, average="macro")
        print(f"loss={running_loss / len(train_loader.dataset):.4f} val_acc={val_acc:.4f} val_macro_f1={val_f1:.4f}")

        if val_f1 > best_f1:
            best_f1 = val_f1
            torch.save({
                "model_state_dict": model.state_dict(),
                "class_names": class_names,
                "image_size": 224,
            }, output)

    checkpoint = torch.load(output, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    test_true, test_pred = predict(model, test_loader, device)
    print(f"TEST accuracy={accuracy_score(test_true, test_pred):.4f}")
    print(f"TEST macro_f1={f1_score(test_true, test_pred, average='macro'):.4f}")

    output.with_suffix(".json").write_text(json.dumps({
        "dataset": args.dataset,
        "config": args.config,
        "classes": class_names,
        "train": len(train_idx),
        "validation": len(val_idx),
        "test": len(test_idx),
        "best_validation_macro_f1": best_f1,
    }, indent=2))


def predict(model, loader, device):
    model.eval()
    true, pred = [], []
    with torch.no_grad():
        for x, y in loader:
            logits = model(x.to(device))
            pred.extend(logits.argmax(1).cpu().numpy())
            true.extend(y.numpy())
    return true, pred


if __name__ == "__main__":
    main()
