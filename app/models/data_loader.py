"""Data loader module for bank marketing dataset.

Provides functions to load train and test data with proper error handling
and data validation.
"""

from pathlib import Path

import pandas as pd

# Feature columns (present in both train and test data)
FEATURE_COLUMNS = [
    "id",
    "age",
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "poutcome",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]

# Full columns including target variable (for train data)
TRAIN_COLUMNS = FEATURE_COLUMNS + ["subscribe"]

# Target column and the value meaning "subscribed".
TARGET_COLUMN = "subscribe"
TARGET_POSITIVE = "yes"

# Feature schema used for model training and prediction (excludes id/target).
# Single source of truth shared by ml.train and models.predictor.
CATEGORICAL_FEATURES = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]
NUMERIC_FEATURES = [
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]
MODEL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

# Missing value markers in the dataset
MISSING_VALUE_MARKERS = ["unknown", "nonexistent", ""]


def load_train_data(data_dir: Path | None = None) -> pd.DataFrame:
    """Load training data from CSV file.

    Args:
        data_dir: Path to data directory. Defaults to ./data relative to project root.

    Returns:
        DataFrame with training data including target variable.

    Raises:
        FileNotFoundError: If train.csv file does not exist.
        ValueError: If file is empty or has invalid format.

    Examples:
        >>> df = load_train_data()
        >>> len(df) > 0
        True
        >>> "subscribe" in df.columns
        True
    """
    if data_dir is None:
        data_dir = Path(__file__).parent.parent.parent / "data"

    train_path = data_dir / "train.csv"
    return _load_csv(train_path, expected_columns=TRAIN_COLUMNS)


def load_test_data(data_dir: Path | None = None) -> pd.DataFrame:
    """Load test data from CSV file.

    Note: Test data does not include the 'subscribe' target variable.

    Args:
        data_dir: Path to data directory. Defaults to ./data relative to project root.

    Returns:
        DataFrame with test data (features only, no target variable).

    Raises:
        FileNotFoundError: If test.csv file does not exist.
        ValueError: If file is empty or has invalid format.

    Examples:
        >>> df = load_test_data()
        >>> len(df) > 0
        True
        >>> "subscribe" not in df.columns
        True
    """
    if data_dir is None:
        data_dir = Path(__file__).parent.parent.parent / "data"

    test_path = data_dir / "test.csv"
    return _load_csv(test_path, expected_columns=FEATURE_COLUMNS)


def _load_csv(file_path: Path, expected_columns: list[str]) -> pd.DataFrame:
    """Internal function to load and validate CSV file.

    Args:
        file_path: Path to CSV file.
        expected_columns: List of expected column names.

    Returns:
        DataFrame with loaded and validated data.

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If file is empty or has invalid format.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")

    # Read CSV
    df = pd.read_csv(file_path)

    # Validate file is not empty
    if len(df) == 0:
        raise ValueError(f"Data file is empty: {file_path}")

    # Validate columns
    missing_columns = set(expected_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing expected columns: {missing_columns}. " f"Found columns: {list(df.columns)}"
        )

    return df


def get_missing_value_mask(df: pd.DataFrame, column: str) -> pd.Series:
    """Get boolean mask indicating rows with missing values in specified column.

    Args:
        df: Input DataFrame.
        column: Column name to check for missing values.

    Returns:
        Boolean Series where True indicates missing value.

    Examples:
        >>> df = load_train_data()
        >>> mask = get_missing_value_mask(df, "education")
        >>> mask.dtype
        dtype('bool')
    """
    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")

    return df[column].isin(MISSING_VALUE_MARKERS)


def get_column_statistics(df: pd.DataFrame, column: str) -> dict:
    """Get statistics for a column.

    For categorical columns: value counts (including missing).
    For numerical columns: basic statistics.

    Args:
        df: Input DataFrame.
        column: Column name to analyze.

    Returns:
        Dictionary with column statistics.

    Examples:
        >>> df = load_train_data()
        >>> stats = get_column_statistics(df, "age")
        >>> "mean" in stats
        True
    """
    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")

    col_data = df[column]

    if col_data.dtype in ["int64", "float64"]:
        return {
            "count": int(col_data.count()),
            "mean": float(col_data.mean()),
            "std": float(col_data.std()),
            "min": float(col_data.min()),
            "max": float(col_data.max()),
        }
    else:
        value_counts = col_data.value_counts(dropna=False).to_dict()
        # Convert keys to strings for JSON serialization
        return {
            "count": int(col_data.count()),
            "unique": int(col_data.nunique()),
            "value_counts": {str(k): int(v) for k, v in value_counts.items()},
        }
