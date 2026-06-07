"""Offline training script for the subscription prediction model.

Builds a scikit-learn Pipeline (OneHot-encoded categoricals + passthrough
numerics -> RandomForest) and persists it together with the feature schema so
the online predictor is fully self-contained.

Usage:
    python -m app.ml.train                 # train and save (skip if model exists)
    python -m app.ml.train --overwrite     # retrain even if a model exists
    python -m app.ml.train --check-auc 0.7 # fail if test AUC below threshold
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.models.data_loader import (
    CATEGORICAL_FEATURES,
    MODEL_FEATURES,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
    TARGET_POSITIVE,
    load_train_data,
)

RANDOM_STATE = 42
TEST_SIZE = 0.2
MODEL_DIR = Path(__file__).parent / "model"
MODEL_PATH = MODEL_DIR / "model.pkl"


def build_pipeline() -> Pipeline:
    """Build the preprocessing + classifier pipeline.

    OneHot-encodes categorical features (ignoring unseen categories at predict
    time) and passes numeric features through unchanged.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
            ("num", "passthrough", NUMERIC_FEATURES),
        ]
    )
    classifier = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    return Pipeline([("preprocess", preprocessor), ("model", classifier)])


def _prepare_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Split a training DataFrame into feature matrix X and binary target y."""
    x = df[MODEL_FEATURES].copy()
    y = (df[TARGET_COLUMN] == TARGET_POSITIVE).astype(int)
    return x, y


def train_model(df: pd.DataFrame) -> tuple[Pipeline, dict]:
    """Train the pipeline and return it together with evaluation metrics.

    Args:
        df: Training DataFrame including the target column.

    Returns:
        Tuple of (fitted pipeline, metrics dict with auc/accuracy/report).
    """
    x, y = _prepare_xy(df)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)

    proba = pipeline.predict_proba(x_test)[:, 1]
    preds = pipeline.predict(x_test)
    metrics = {
        "auc": float(roc_auc_score(y_test, proba)),
        "accuracy": float(accuracy_score(y_test, preds)),
        "report": classification_report(y_test, preds, digits=4),
        "n_train": int(len(x_train)),
        "n_test": int(len(x_test)),
    }
    return pipeline, metrics


def save_model(pipeline: Pipeline, path: Path = MODEL_PATH) -> Path:
    """Persist the pipeline plus feature schema to a pickle file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "pipeline": pipeline,
        "categorical_features": CATEGORICAL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "feature_columns": MODEL_FEATURES,
        "target_positive": TARGET_POSITIVE,
        "random_state": RANDOM_STATE,
    }
    joblib.dump(payload, path)
    return path


def main() -> None:
    """CLI entry point for offline training."""
    parser = argparse.ArgumentParser(description="Train subscription prediction model.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Retrain and overwrite even if a model file already exists.",
    )
    parser.add_argument(
        "--check-auc",
        type=float,
        default=None,
        help="Fail with non-zero exit if test AUC is below this threshold.",
    )
    args = parser.parse_args()

    if MODEL_PATH.exists() and not args.overwrite:
        print(f"Model already exists at {MODEL_PATH}; use --overwrite to retrain.")
        return

    print("Loading training data...")
    df = load_train_data()
    print(f"Loaded {len(df)} rows.")

    print("Training model (RandomForest)...")
    pipeline, metrics = train_model(df)

    print("\n=== Evaluation (held-out test split) ===")
    print(f"Train/Test sizes : {metrics['n_train']} / {metrics['n_test']}")
    print(f"ROC AUC          : {metrics['auc']:.4f}")
    print(f"Accuracy         : {metrics['accuracy']:.4f}")
    print("Classification report:")
    print(metrics["report"])

    if args.check_auc is not None and metrics["auc"] < args.check_auc:
        raise SystemExit(f"AUC {metrics['auc']:.4f} below required threshold {args.check_auc:.4f}")

    path = save_model(pipeline)
    print(f"Saved model to {path}")


if __name__ == "__main__":
    main()
