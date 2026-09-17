"""Optionally fetch the trained ChilliProfit model before API startup."""

import hashlib
import os
from pathlib import Path
from urllib.request import Request, urlopen

MODEL_PATH = Path(os.getenv("CHILLIPROFIT_MODEL_PATH", "ml/artifacts/chilli_model.pt"))
MODEL_URL = os.getenv("CHILLIPROFIT_MODEL_URL", "").strip()
EXPECTED_SHA256 = os.getenv("CHILLIPROFIT_MODEL_SHA256", "").strip().lower()


def main() -> None:
    if MODEL_PATH.exists():
        print(f"Model already present: {MODEL_PATH}")
        return

    if not MODEL_URL:
        print("No CHILLIPROFIT_MODEL_URL configured; starting without a trained model.")
        return

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading ChilliProfit model from {MODEL_URL}")
    request = Request(MODEL_URL, headers={"User-Agent": "ChilliProfit-AI/1.0"})
    digest = hashlib.sha256()
    temporary = MODEL_PATH.with_suffix(MODEL_PATH.suffix + ".download")

    try:
        with urlopen(request, timeout=120) as response, temporary.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                digest.update(chunk)

        actual_sha256 = digest.hexdigest()
        if EXPECTED_SHA256 and actual_sha256 != EXPECTED_SHA256:
            raise RuntimeError(
                f"Model SHA256 mismatch: expected {EXPECTED_SHA256}, got {actual_sha256}"
            )

        temporary.replace(MODEL_PATH)
        print(f"Model downloaded successfully: {MODEL_PATH}")
        print(f"Model SHA256: {actual_sha256}")
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


if __name__ == "__main__":
    main()
