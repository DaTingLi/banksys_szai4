"""Tests for the model training module.

Uses a small synthetic dataset to keep tests fast and avoid depending on the
full data file. Verifies pipeline construction, X/y preparation, end-to-end
training metrics, and model persistence (with feature schema).
"""

import joblib
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from app.ml import train
from app.models.data_loader import CATEGORICAL_FEATURES, MODEL_FEATURES, NUMERIC_FEATURES


@pytest.fixture
def synthetic_df():
    """Synthetic dataset with a learnable signal and both target classes."""
    rows = []
    for i in range(60):
        positive = i % 3 == 0
        rows.append(
            {
                "job": "student" if positive else "admin.",
                "marital": "single" if positive else "married",
                "education": "university.degree",
                "default": "no",
                "housing": "yes" if positive else "no",
                "loan": "no",
                "contact": "cellular",
                "month": "may",
                "day_of_week": "mon",
                "poutcome": "success" if positive else "failure",
                "age": 25 if positive else 50,
                "duration": 800 if positive else 100,
                "campaign": 1 if positive else 3,
                "pdays": 5 if positive else 999,
                "previous": 2 if positive else 0,
                "emp_var_rate": -1.8 if positive else 1.4,
                "cons_price_index": 92.0,
                "cons_conf_index": -40.0,
                "lending_rate3m": 1.0,
                "nr_employed": 5000.0,
                "subscribe": "yes" if positive else "no",
            }
        )
    return pd.DataFrame(rows)


class TestBuildPipeline:
    def test_returns_pipeline(self):
        assert isinstance(train.build_pipeline(), Pipeline)

    def test_pipeline_has_expected_steps(self):
        pipeline = train.build_pipeline()
        assert "preprocess" in pipeline.named_steps
        assert "model" in pipeline.named_steps


class TestPrepareXy:
    def test_x_has_model_features(self, synthetic_df):
        x, _ = train._prepare_xy(synthetic_df)
        assert list(x.columns) == MODEL_FEATURES

    def test_y_is_binary(self, synthetic_df):
        _, y = train._prepare_xy(synthetic_df)
        assert set(y.unique()).issubset({0, 1})

    def test_y_positive_count(self, synthetic_df):
        _, y = train._prepare_xy(synthetic_df)
        assert int(y.sum()) == 20


class TestTrainModel:
    def test_returns_fitted_pipeline_and_metrics(self, synthetic_df):
        pipeline, metrics = train.train_model(synthetic_df)
        assert isinstance(pipeline, Pipeline)
        assert "auc" in metrics and "accuracy" in metrics

    def test_metrics_within_range(self, synthetic_df):
        _, metrics = train.train_model(synthetic_df)
        assert 0.0 <= metrics["auc"] <= 1.0
        assert 0.0 <= metrics["accuracy"] <= 1.0

    def test_reproducible(self, synthetic_df):
        _, metrics_a = train.train_model(synthetic_df)
        _, metrics_b = train.train_model(synthetic_df)
        assert metrics_a["auc"] == metrics_b["auc"]


class TestSaveModel:
    def test_save_creates_file(self, synthetic_df, tmp_path):
        pipeline, _ = train.train_model(synthetic_df)
        out = tmp_path / "model.pkl"
        saved = train.save_model(pipeline, path=out)
        assert saved.exists()

    def test_saved_payload_schema(self, synthetic_df, tmp_path):
        pipeline, _ = train.train_model(synthetic_df)
        out = tmp_path / "model.pkl"
        train.save_model(pipeline, path=out)
        payload = joblib.load(out)
        assert payload["categorical_features"] == CATEGORICAL_FEATURES
        assert payload["numeric_features"] == NUMERIC_FEATURES
        assert isinstance(payload["pipeline"], Pipeline)
