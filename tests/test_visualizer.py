"""Tests for the visualizer module.

Computation helpers are tested with a small in-memory DataFrame (no dependency
on the real data files). Figure builders are smoke-tested to confirm they
return Plotly figures without raising.
"""

import pandas as pd
import plotly.graph_objects as go
import pytest

from app.models import visualizer


@pytest.fixture
def sample_df():
    """Small, hand-built dataset with a known subscribe distribution."""
    return pd.DataFrame(
        {
            "age": [23, 30, 41, 52, 67, 38, 29, 45],
            "job": [
                "admin.",
                "admin.",
                "services",
                "services",
                "retired",
                "admin.",
                "blue-collar",
                "services",
            ],
            "duration": [100, 200, 300, 400, 500, 150, 250, 350],
            "subscribe": ["no", "yes", "no", "yes", "yes", "no", "no", "no"],
        }
    )


class TestComputeOverview:
    def test_overview_counts_and_rate(self, sample_df):
        result = visualizer.compute_overview(sample_df)
        assert result["total_records"] == 8
        assert result["subscribed"] == 3
        assert result["not_subscribed"] == 5
        assert result["subscribe_rate"] == pytest.approx(3 / 8)

    def test_overview_feature_count(self, sample_df):
        result = visualizer.compute_overview(sample_df)
        assert result["feature_count"] == 4

    def test_overview_missing_target_raises(self):
        df = pd.DataFrame({"age": [1, 2]})
        with pytest.raises(ValueError, match="Target column"):
            visualizer.compute_overview(df)


class TestComputeValueCounts:
    def test_value_counts_sums_to_total(self, sample_df):
        result = visualizer.compute_value_counts(sample_df, "job")
        assert result["count"].sum() == len(sample_df)

    def test_value_counts_columns(self, sample_df):
        result = visualizer.compute_value_counts(sample_df, "job")
        assert list(result.columns) == ["job", "count"]

    def test_value_counts_admin_count(self, sample_df):
        result = visualizer.compute_value_counts(sample_df, "job")
        admin_row = result[result["job"] == "admin."]
        assert int(admin_row["count"].iloc[0]) == 3

    def test_value_counts_missing_column_raises(self, sample_df):
        with pytest.raises(ValueError, match="Column not found"):
            visualizer.compute_value_counts(sample_df, "nonexistent")


class TestSubscribeRateByCategory:
    def test_rate_values(self, sample_df):
        result = visualizer.compute_subscribe_rate_by_category(sample_df, "job")
        retired = result[result["job"] == "retired"]
        assert retired["rate"].iloc[0] == pytest.approx(1.0)
        admin = result[result["job"] == "admin."]
        assert admin["rate"].iloc[0] == pytest.approx(1 / 3)

    def test_rate_sorted_descending(self, sample_df):
        result = visualizer.compute_subscribe_rate_by_category(sample_df, "job")
        rates = result["rate"].tolist()
        assert rates == sorted(rates, reverse=True)

    def test_totals_match(self, sample_df):
        result = visualizer.compute_subscribe_rate_by_category(sample_df, "job")
        assert result["total"].sum() == len(sample_df)

    def test_missing_target_raises(self):
        df = pd.DataFrame({"job": ["a", "b"]})
        with pytest.raises(ValueError, match="Target column"):
            visualizer.compute_subscribe_rate_by_category(df, "job")


class TestComputeAgeGroups:
    def test_age_group_counts_sum(self, sample_df):
        result = visualizer.compute_age_groups(sample_df)
        assert result["count"].sum() == len(sample_df)

    def test_age_group_has_rate_column(self, sample_df):
        result = visualizer.compute_age_groups(sample_df)
        assert "rate" in result.columns
        assert (result["rate"] >= 0).all() and (result["rate"] <= 1).all()

    def test_age_group_custom_bins(self, sample_df):
        result = visualizer.compute_age_groups(
            sample_df, bins=[0, 40, 120], labels=["young", "old"]
        )
        assert set(result["age_group"]) == {"young", "old"}

    def test_age_group_invalid_labels_raises(self, sample_df):
        with pytest.raises(ValueError, match="labels length"):
            visualizer.compute_age_groups(sample_df, bins=[0, 50, 120], labels=["only_one"])


class TestNumericSummary:
    def test_summary_keys(self, sample_df):
        result = visualizer.compute_numeric_summary(sample_df, "age")
        for key in ["count", "mean", "std", "min", "q25", "median", "q75", "max"]:
            assert key in result

    def test_summary_values(self, sample_df):
        result = visualizer.compute_numeric_summary(sample_df, "duration")
        assert result["min"] == 100.0
        assert result["max"] == 500.0
        assert result["count"] == 8

    def test_summary_non_numeric_raises(self, sample_df):
        with pytest.raises(ValueError, match="not numeric"):
            visualizer.compute_numeric_summary(sample_df, "job")

    def test_summary_missing_column_raises(self, sample_df):
        with pytest.raises(ValueError, match="Column not found"):
            visualizer.compute_numeric_summary(sample_df, "nope")


class TestFigureBuilders:
    def test_build_subscribe_pie(self, sample_df):
        assert isinstance(visualizer.build_subscribe_pie(sample_df), go.Figure)

    def test_build_category_bar(self, sample_df):
        assert isinstance(visualizer.build_category_bar(sample_df, "job"), go.Figure)

    def test_build_subscribe_rate_bar(self, sample_df):
        assert isinstance(visualizer.build_subscribe_rate_bar(sample_df, "job"), go.Figure)

    def test_build_age_histogram(self, sample_df):
        assert isinstance(visualizer.build_age_histogram(sample_df), go.Figure)

    def test_build_numeric_histogram(self, sample_df):
        assert isinstance(visualizer.build_numeric_histogram(sample_df, "duration"), go.Figure)
