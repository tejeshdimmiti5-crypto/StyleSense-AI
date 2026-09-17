# ChilliProfit AI — ML training

## Dataset

The default training script uses the **raw COLD chilli-leaf dataset** from Hugging Face:

`Project-AgML/COLD_chili_leaf_disease_classification`

The raw subset contains 532 original images in five classes: `cercospora`, `healthy`, `mites_and_trips`, `nutritional`, and `powdery mildew`. The source also provides a much larger augmented subset, but this project starts from original images and performs augmentation only on the training split to reduce validation/test leakage. citeturn1view1

A second dataset is available from the Krishna River Basin, covering districts including Guntur, Prakasam, Krishna and Kurnool in Andhra Pradesh. It reports 1,856 original images across six classes and is licensed CC BY 4.0. We can add this as the next training source after verifying its downloadable file structure. citeturn1view0

## Train locally

```bash
cd ml
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python train.py
```

For Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python train.py
```

The best checkpoint is written to:

`ml/artifacts/chilli_model.pt`

Metrics metadata is written beside it as:

`ml/artifacts/chilli_model.json`

## Important

The model is a research prototype, not a clinical/agricultural diagnostic authority. Test performance must be measured on held-out images, and later we should validate with field images collected by the project team before making treatment recommendations.
