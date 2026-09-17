"""Prepare the public chilli datasets used by ChilliProfit AI.

The primary COLD dataset is downloaded automatically through Hugging Face.
The Krishna River Basin dataset is intentionally kept as an external
validation set and must be downloaded manually from its Mendeley page.
Large image archives are not committed to GitHub.
"""

from pathlib import Path
from datasets import load_dataset

COLD_REPO = "Project-AgML/COLD_chili_leaf_disease_classification"
OUTPUT = Path("ml/data/cold_raw")


def download_cold():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ds = load_dataset(COLD_REPO, "raw", split="train")
    ds.save_to_disk(str(OUTPUT))
    print(f"Saved {len(ds)} original COLD images to {OUTPUT}")
    print("Classes:", ds.features["label"].names)


def print_external_dataset_instructions():
    print("\nKrishna River Basin external validation dataset:")
    print("https://data.mendeley.com/datasets/ymt8k9bjkn/3")
    print("Download the ORIGINAL dataset, not the augmented copy.")
    print("Place the extracted class folders under:")
    print("ml/data/krishna_basin/")
    print("Do not commit the images to GitHub.")


if __name__ == "__main__":
    download_cold()
    print_external_dataset_instructions()
