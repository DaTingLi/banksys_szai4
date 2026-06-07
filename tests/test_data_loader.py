"""Tests for data_loader module."""

import pandas as pd
import pytest

from app.models.data_loader import (
    FEATURE_COLUMNS,
    TRAIN_COLUMNS,
    get_column_statistics,
    get_missing_value_mask,
    load_test_data,
    load_train_data,
)


class TestLoadTrainData:
    """Test suite for load_train_data function."""

    def test_load_train_data_returns_dataframe(self):
        """Test that load_train_data returns a pandas DataFrame."""
        df = load_train_data()
        assert isinstance(df, pd.DataFrame)

    def test_load_train_data_has_expected_columns(self):
        """Test that loaded data has all expected columns."""
        df = load_train_data()
        assert list(df.columns) == TRAIN_COLUMNS

    def test_load_train_data_not_empty(self):
        """Test that loaded data is not empty."""
        df = load_train_data()
        assert len(df) > 0

    def test_load_train_data_has_target_column(self):
        """Test that 'subscribe' column exists."""
        df = load_train_data()
        assert "subscribe" in df.columns

    def test_load_train_data_from_custom_dir(self, tmp_path):
        """Test loading from custom data directory."""
        # Create temporary train.csv
        train_data = pd.DataFrame({col: ["test"] for col in TRAIN_COLUMNS})
        train_path = tmp_path / "train.csv"
        train_data.to_csv(train_path, index=False)

        df = load_train_data(data_dir=tmp_path)
        assert len(df) == 1
        assert df.iloc[0]["age"] == "test"


class TestLoadTestData:
    """Test suite for load_test_data function."""

    def test_load_test_data_returns_dataframe(self):
        """Test that load_test_data returns a pandas DataFrame."""
        df = load_test_data()
        assert isinstance(df, pd.DataFrame)

    def test_load_test_data_has_feature_columns(self):
        """Test that loaded data has feature columns only (no target)."""
        df = load_test_data()
        assert list(df.columns) == FEATURE_COLUMNS
        assert "subscribe" not in df.columns

    def test_load_test_data_not_empty(self):
        """Test that loaded data is not empty."""
        df = load_test_data()
        assert len(df) > 0


class TestErrorHandling:
    """Test suite for error handling."""

    def test_load_train_data_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is raised when file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Data file not found"):
            load_train_data(data_dir=tmp_path)

    def test_load_test_data_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is raised when file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Data file not found"):
            load_test_data(data_dir=tmp_path)

    def test_load_empty_file_raises_error(self, tmp_path):
        """Test that ValueError is raised for empty file."""
        empty_path = tmp_path / "train.csv"
        empty_path.write_text("id,age\n")  # Header only

        with pytest.raises(ValueError, match="Data file is empty"):
            load_train_data(data_dir=tmp_path)

    def test_load_invalid_columns_raises_error(self, tmp_path):
        """Test that ValueError is raised for invalid columns."""
        invalid_path = tmp_path / "train.csv"
        invalid_path.write_text("wrong,columns\n1,2\n")

        with pytest.raises(ValueError, match="Missing expected columns"):
            load_train_data(data_dir=tmp_path)


class TestMissingValueMask:
    """Test suite for get_missing_value_mask function."""

    def test_returns_boolean_series(self):
        """Test that function returns boolean Series."""
        df = load_train_data()
        mask = get_missing_value_mask(df, "education")
        assert mask.dtype == bool

    def test_invalid_column_raises_error(self):
        """Test that ValueError is raised for invalid column."""
        df = load_train_data()
        with pytest.raises(ValueError, match="Column not found"):
            get_missing_value_mask(df, "nonexistent_column")

    def test_detects_missing_values(self):
        """Test that missing values are correctly detected."""
        df = pd.DataFrame({"col": ["known", "unknown", "nonexistent", ""]})
        mask = get_missing_value_mask(df, "col")
        # First value should not be marked as missing
        assert not mask.iloc[0]
        # Rest should be marked as missing
        assert mask.iloc[1:].all()
        assert mask.sum() == 3


class TestColumnStatistics:
    """Test suite for get_column_statistics function."""

    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing."""
        return pd.DataFrame(
            {
                "age": [25, 30, 35, 40, 45],
                "job": ["admin.", "blue-collar", "unknown", "admin.", "blue-collar"],
            }
        )

    def test_returns_statistics_for_numeric_column(self, sample_df):
        """Test that statistics are returned for numeric columns."""
        stats = get_column_statistics(sample_df, "age")
        assert "mean" in stats
        assert "std" in stats
        assert "min" in stats
        assert "max" in stats
        assert stats["mean"] == 35.0

    def test_returns_statistics_for_categorical_column(self, sample_df):
        """Test that statistics are returned for categorical columns."""
        stats = get_column_statistics(sample_df, "job")
        assert "count" in stats
        assert "unique" in stats
        assert "value_counts" in stats
        assert stats["unique"] == 3

    def test_invalid_column_raises_error(self):
        """Test that ValueError is raised for invalid column."""
        df = load_train_data()
        with pytest.raises(ValueError, match="Column not found"):
            get_column_statistics(df, "nonexistent_column")

    def test_real_data_age_statistics(self):
        """Test statistics on real age data."""
        df = load_train_data()
        stats = get_column_statistics(df, "age")
        assert stats["min"] >= 0
        assert stats["max"] <= 120
        assert stats["count"] == len(df)


class TestIntegration:
    """Integration tests for data loader."""

    def test_train_has_more_columns_than_test(self):
        """Test that train data has target column while test data does not."""
        train_df = load_train_data()
        test_df = load_test_data()
        # Train has subscribe column
        assert "subscribe" in train_df.columns
        # Test does not have subscribe column
        assert "subscribe" not in test_df.columns
        # Test has all feature columns
        assert set(test_df.columns) == set(FEATURE_COLUMNS)

    def test_data_dimensions_reasonable(self):
        """Test that data dimensions are reasonable."""
        train_df = load_train_data()
        test_df = load_test_data()
        # Both should have at least 1000 rows
        assert len(train_df) > 1000
        assert len(test_df) > 1000
        # Train has 22 columns, test has 21 columns
        assert len(train_df.columns) == 22
        assert len(test_df.columns) == 21
