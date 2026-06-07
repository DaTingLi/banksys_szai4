"""Tests for the predictor module.

A small model is trained on synthetic data and saved to a temp path, so tests
never depend on the real (gitignored) model artifact.
"""

import time

import pandas as pd
import pytest

from app.ml import train
from app.models import predictor
from app.models.data_loader import MODEL_FEATURES


def _make_features(positive: bool = True) -> dict:
    """Build a complete, valid feature dict for one customer."""
    return {
        "job": "student" if positive else "admin.",
        "marital": "single" if positive else "married",
        "education": "university.degree",
        "default": "no",
        "housing": "yes",
        "loan": "no",
        "contact": "cellular",
        "month": "may",
        "day_of_week": "mon",
        "poutcome": "success" if positive else "failure",
        "age": 25 if positive else 50,
        "duration": 800 if positive else 100,
        "campaign": 1,
        "pdays": 5 if positive else 999,
        "previous": 2 if positive else 0,
        "emp_var_rate": -1.8 if positive else 1.4,
        "cons_price_index": 92.0,
        "cons_conf_index": -40.0,
        "lending_rate3m": 1.0,
        "nr_employed": 5000.0,
    }


@pytest.fixture
def model_path(tmp_path):
    """Train a tiny model on synthetic data and return its file path as str."""
    rows = [_make_features(positive=(i % 3 == 0)) for i in range(60)]
    df = pd.DataFrame(rows)
    df["subscribe"] = ["yes" if i % 3 == 0 else "no" for i in range(60)]
    pipeline, _ = train.train_model(df)
    out = tmp_path / "model.pkl"
    train.save_model(pipeline, path=out)
    return str(out)


class TestLoadModel:
    def test_missing_model_raises(self, tmp_path):
        missing = str(tmp_path / "nope.pkl")
        with pytest.raises(predictor.ModelNotFoundError):
            predictor.load_model(missing)

    def test_load_returns_payload(self, model_path):
        payload = predictor.load_model(model_path)
        assert "pipeline" in payload
        assert payload["feature_columns"] == MODEL_FEATURES


class TestPredict:
    def test_returns_expected_keys(self, model_path):
        result = predictor.predict(_make_features(), model_path=model_path)
        assert set(result.keys()) == {"subscribe", "probability", "confidence"}

    def test_types(self, model_path):
        result = predictor.predict(_make_features(), model_path=model_path)
        assert isinstance(result["subscribe"], bool)
        assert isinstance(result["probability"], float)
        assert isinstance(result["confidence"], str)

    def test_probability_in_range(self, model_path):
        result = predictor.predict(_make_features(), model_path=model_path)
        assert 0.0 <= result["probability"] <= 1.0

    def test_subscribe_consistent_with_probability(self, model_path):
        result = predictor.predict(_make_features(), model_path=model_path)
        assert result["subscribe"] == (result["probability"] >= 0.5)

    def test_missing_feature_raises(self, model_path):
        features = _make_features()
        del features["age"]
        with pytest.raises(ValueError, match="Missing required features"):
            predictor.predict(features, model_path=model_path)

    def test_invalid_numeric_raises(self, model_path):
        features = _make_features()
        features["age"] = "not-a-number"
        with pytest.raises(ValueError, match="must be numeric"):
            predictor.predict(features, model_path=model_path)

    def test_unknown_category_handled(self, model_path):
        features = _make_features()
        features["job"] = "astronaut"  # unseen category
        result = predictor.predict(features, model_path=model_path)
        assert 0.0 <= result["probability"] <= 1.0

    def test_response_under_one_second(self, model_path):
        predictor.predict(_make_features(), model_path=model_path)  # warm cache
        start = time.perf_counter()
        predictor.predict(_make_features(), model_path=model_path)
        assert (time.perf_counter() - start) < 1.0


class TestConfidenceLabel:
    @pytest.mark.parametrize(
        "prob,expected",
        [
            (0.95, "high"),
            (0.05, "high"),
            (0.7, "medium"),
            (0.3, "medium"),
            (0.5, "low"),
            (0.55, "low"),
        ],
    )
    def test_confidence_labels(self, prob, expected):
        assert predictor._confidence_label(prob) == expected
