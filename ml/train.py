"""Train a chilli-leaf disease classifier with reproducible evaluation."""

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from datasets import load_dataset
from PIL import Image
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from tqdm import tqdm

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)


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


def evaluate(model, loader, device):
    model.eval()
    true, pred = [], []
    with torch.inference_mode():
        for x, y in loader:
            logits = model(x.to(device))
            pred.extend(logits.argmax(1).cpu().numpy())
            true.extend(y.numpy())
    return np.asarray(true), np.asarray(pred)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="Project-AgML/COLD_chili_leaf_disease_classification")
    parser.add_argument("--config", default="raw")
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--output", default="ml/artifacts/chilli_model.pt")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    print(f"Seed: {SEED}")

    ds = load_dataset(args.dataset, args.config, split="train")
    class_names = ds.features["label"].names
    labels = np.asarray(ds["label"])

    train_idx, temp_idx = train_test_split(
        np.arange(len(ds)), test_size=0.30, random_state=SEED, stratify=labels
    )
    temp_labels = labels[temp_idx]
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

    train_labels = labels[train_idx].tolist()
    val_labels = labels[val_idx].tolist()
    test_labels = labels[test_idx].tolist()
    train_loader = DataLoader(LeafDataset(ds.select(train_idx.tolist()), train_labels, train_tfms), batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(LeafDataset(ds.select(val_idx.tolist()), val_labels, eval_tfms), batch_size=args.batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(LeafDataset(ds.select(test_idx.tolist()), test_labels, eval_tfms), batch_size=args.batch_size, shuffle=False, num_workers=0)

    model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(class_names))
    model.to(device)

    counts = np.bincount(train_labels, minlength=len(class_names))
    weights = len(train_labels) / (len(class_names) * np.maximum(counts, 1))
    criterion = nn.CrossEntropyLoss(weight=torch.tensor(weights, dtype=torch.float32, device=device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=1)

    best_f1 = -1.0
    best_epoch = 0
    stale_epochs = 0
    history = []
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(args.epochs):
        model.train()
        running_loss = 0.0
        for x, y in tqdm(train_loader, desc=f"Epoch {epoch + 1}/{args.epochs}"):
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * x.size(0)

        val_true, val_pred = evaluate(model, val_loader, device)
        val_acc = accuracy_score(val_true, val_pred)
        val_f1 = f1_score(val_true, val_pred, average="macro")
        train_loss = running_loss / len(train_loader.dataset)
        scheduler.step(val_f1)
        record = {"epoch": epoch + 1, "train_loss": train_loss, "val_accuracy": val_acc, "val_macro_f1": val_f1, "learning_rate": optimizer.param_groups[0]["lr"]}
        history.append(record)
        print(f"loss={train_loss:.4f} val_acc={val_acc:.4f} val_macro_f1={val_f1:.4f}")

        if val_f1 > best_f1:
            best_f1 = val_f1
            best_epoch = epoch + 1
            stale_epochs = 0
            torch.save({
                "model_state_dict": model.state_dict(),
                "class_names": class_names,
                "image_size": 224,
                "seed": SEED,
                "dataset": args.dataset,
                "config": args.config,
                "best_validation_macro_f1": best_f1,
                "best_epoch": best_epoch,
            }, output)
        else:
            stale_epochs += 1
            if stale_epochs >= args.patience:
                print(f"Early stopping after {epoch + 1} epochs.")
                break

    checkpoint = torch.load(output, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    test_true, test_pred = evaluate(model, test_loader, device)
    test_acc = accuracy_score(test_true, test_pred)
    test_f1 = f1_score(test_true, test_pred, average="macro")
    precision, recall, f1_values, support = precision_recall_fscore_support(
        test_true, test_pred, labels=np.arange(len(class_names)), zero_division=0
    )

    print(f"TEST accuracy={test_acc:.4f}")
    print(f"TEST macro_f1={test_f1:.4f}")
    print(classification_report(test_true, test_pred, labels=np.arange(len(class_names)), target_names=class_names, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(test_true, test_pred, labels=np.arange(len(class_names))))

    metrics = {
        "dataset": args.dataset,
        "config": args.config,
        "classes": class_names,
        "seed": SEED,
        "device": device,
        "train": len(train_idx),
        "validation": len(val_idx),
        "test": len(test_idx),
        "best_epoch": best_epoch,
        "best_validation_macro_f1": best_f1,
        "test_accuracy": test_acc,
        "test_macro_f1": test_f1,
        "per_class": {
            name: {"precision": float(precision[i]), "recall": float(recall[i]), "f1": float(f1_values[i]), "support": int(support[i])}
            for i, name in enumerate(class_names)
        },
        "confusion_matrix": confusion_matrix(test_true, test_pred, labels=np.arange(len(class_names))).tolist(),
        "history": history,
    }
    output.with_suffix(".json").write_text(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
