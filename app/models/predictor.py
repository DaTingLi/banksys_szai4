"""Online prediction service for subscription likelihood.

Loads the offline-trained pipeline (with its feature schema) and exposes a
single ``predict`` function returning a friendly result dict. The model is
loaded lazily and cached so repeated predictions stay well under 1s.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

try:
    import joblib
except ImportError:  # pragma: no cover - joblib ships with scikit-learn
    joblib = None

DEFAULT_MODEL_PATH = Path(__file__).parent.parent / "ml" / "model" / "model.pkl"

# Probability thresholds for the human-readable confidence label.
_HIGH_CONFIDENCE = 0.8
_MEDIUM_CONFIDENCE = 0.6


class ModelNotFoundError(FileNotFoundError):
    """Raised when the trained model file is missing."""


@lru_cache(maxsize=4)
def load_model(model_path: str | None = None) -> dict:
    """Load and cache the trained model payload.

    Args:
        model_path: Optional path to the model pickle. Defaults to the
            standard ``app/ml/model/model.pkl`` location.

    Returns:
        The persisted payload dict (pipeline + feature schema).

    Raises:
        ModelNotFoundError: If the model file does not exist. Train it first
            with ``python -m app.ml.train``.
    """
    path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
    if not path.exists():
        raise ModelNotFoundError(
            f"Model file not found: {path}. Run 'python -m app.ml.train' first."
        )
    return joblib.load(path)


def _confidence_label(probability: float) -> str:
    """Map a probability to a confidence label based on its distance from 0.5."""
    certainty = max(probability, 1.0 - probability)
    if certainty >= _HIGH_CONFIDENCE:
        return "high"
    if certainty >= _MEDIUM_CONFIDENCE:
        return "medium"
    return "low"


def _build_feature_frame(features: dict, payload: dict) -> pd.DataFrame:
    """Build a single-row DataFrame in the exact column order the model expects.

    Args:
        features: Mapping of feature name -> value.
        payload: Loaded model payload containing the feature schema.

    Returns:
        One-row DataFrame with all required feature columns.

    Raises:
        ValueError: If required features are missing or numeric values are not
            convertible to numbers.
    """
    required = payload["feature_columns"]
    missing = [col for col in required if col not in features]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    numeric = set(payload["numeric_features"])
    row = {}
    for col in required:
        value = features[col]
        if col in numeric:
            try:
                row[col] = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Feature '{col}' must be numeric, got {value!r}") from exc
        else:
            row[col] = value

    return pd.DataFrame([row], columns=required)


def predict(features: dict, model_path: str | None = None) -> dict:
    """Predict subscription likelihood for a single customer.

    Args:
        features: Mapping of feature name -> value. Must include every column
            in the model's feature schema. Unknown categorical values are
            handled gracefully by the encoder.
        model_path: Optional override for the model file location.

    Returns:
        Dict with:
            - "subscribe" (bool): predicted positive class.
            - "probability" (float): probability of subscribing, in [0, 1].
            - "confidence" (str): "high" / "medium" / "low".

    Raises:
        ModelNotFoundError: If the model file is missing.
        ValueError: If required features are missing or invalid.
    """
    payload = load_model(model_path)
    pipeline = payload["pipeline"]

    frame = _build_feature_frame(features, payload)
    probability = float(pipeline.predict_proba(frame)[0, 1])

    return {
        "subscribe": probability >= 0.5,
        "probability": probability,
        "confidence": _confidence_label(probability),
    }
