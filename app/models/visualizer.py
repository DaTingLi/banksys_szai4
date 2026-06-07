"""Visualization logic for the bank marketing dataset.

This module separates *computation* (pure functions returning DataFrames/dicts,
easy to unit test) from *rendering* (Plotly figure builders used by the UI page).
The Streamlit page only orchestrates these helpers.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Target column and the value that means "subscribed".
TARGET_COLUMN = "subscribe"
TARGET_POSITIVE = "yes"

# Categorical features available for distribution / subscribe-rate analysis.
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

# Numeric features available for distribution analysis.
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

# Default age buckets for grouped age analysis.
DEFAULT_AGE_BINS = [0, 25, 35, 45, 55, 65, 120]
DEFAULT_AGE_LABELS = ["<25", "25-34", "35-44", "45-54", "55-64", "65+"]


def compute_overview(df: pd.DataFrame) -> dict:
    """Compute high-level dataset overview metrics.

    Args:
        df: Training DataFrame including the target column.

    Returns:
        Dict with total_records, feature_count, subscribed, not_subscribed,
        and subscribe_rate (fraction in [0, 1]).

    Raises:
        ValueError: If the target column is missing.
    """
    _require_target(df)

    total = len(df)
    subscribed = int((df[TARGET_COLUMN] == TARGET_POSITIVE).sum())
    rate = subscribed / total if total else 0.0

    return {
        "total_records": total,
        "feature_count": df.shape[1],
        "subscribed": subscribed,
        "not_subscribed": total - subscribed,
        "subscribe_rate": rate,
    }


def compute_value_counts(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Compute value counts for a categorical column.

    Args:
        df: Input DataFrame.
        column: Categorical column name.

    Returns:
        DataFrame with columns [<column>, "count"], sorted by count desc.

    Raises:
        ValueError: If the column is not present.
    """
    _require_column(df, column)

    counts = df[column].value_counts(dropna=False)
    return pd.DataFrame({column: counts.index.astype(str), "count": counts.to_numpy()}).reset_index(
        drop=True
    )


def compute_subscribe_rate_by_category(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Compute subscription rate per category value.

    Args:
        df: DataFrame including the target column.
        column: Categorical column to group by.

    Returns:
        DataFrame with columns [<column>, "total", "subscribed", "rate"],
        sorted by rate descending. "rate" is a fraction in [0, 1].

    Raises:
        ValueError: If the column or target column is missing.
    """
    _require_target(df)
    _require_column(df, column)

    is_positive = df[TARGET_COLUMN] == TARGET_POSITIVE
    grouped = df.assign(_positive=is_positive).groupby(column, dropna=False)
    result = grouped["_positive"].agg(["count", "sum"]).reset_index()
    result.columns = [column, "total", "subscribed"]
    result["subscribed"] = result["subscribed"].astype(int)
    result["rate"] = result["subscribed"] / result["total"]
    result[column] = result[column].astype(str)

    return result.sort_values("rate", ascending=False).reset_index(drop=True)


def compute_age_groups(
    df: pd.DataFrame,
    bins: list[int] | None = None,
    labels: list[str] | None = None,
) -> pd.DataFrame:
    """Bucket ages and count records (with subscribe rate) per bucket.

    Args:
        df: DataFrame including "age" and the target column.
        bins: Bucket edges; defaults to DEFAULT_AGE_BINS.
        labels: Bucket labels; defaults to DEFAULT_AGE_LABELS.

    Returns:
        DataFrame with columns ["age_group", "count", "subscribed", "rate"],
        ordered by the age bucket order.

    Raises:
        ValueError: If "age" or the target column is missing, or bins/labels
            lengths are inconsistent.
    """
    _require_column(df, "age")
    _require_target(df)

    bins = bins if bins is not None else DEFAULT_AGE_BINS
    labels = labels if labels is not None else DEFAULT_AGE_LABELS
    if len(labels) != len(bins) - 1:
        raise ValueError("labels length must equal len(bins) - 1")

    age_group = pd.cut(df["age"], bins=bins, labels=labels, right=False)
    is_positive = df[TARGET_COLUMN] == TARGET_POSITIVE
    work = pd.DataFrame({"age_group": age_group, "_positive": is_positive})

    grouped = work.groupby("age_group", observed=False)["_positive"]
    result = grouped.agg(["count", "sum"]).reset_index()
    result.columns = ["age_group", "count", "subscribed"]
    result["subscribed"] = result["subscribed"].astype(int)
    result["rate"] = (result["subscribed"] / result["count"]).fillna(0.0)
    result["age_group"] = result["age_group"].astype(str)

    return result


def compute_numeric_summary(df: pd.DataFrame, column: str) -> dict:
    """Compute basic descriptive statistics for a numeric column.

    Args:
        df: Input DataFrame.
        column: Numeric column name.

    Returns:
        Dict with count, mean, std, min, q25, median, q75, max.

    Raises:
        ValueError: If the column is missing or not numeric.
    """
    _require_column(df, column)
    if not pd.api.types.is_numeric_dtype(df[column]):
        raise ValueError(f"Column is not numeric: {column}")

    series = df[column]
    return {
        "count": int(series.count()),
        "mean": float(series.mean()),
        "std": float(series.std()),
        "min": float(series.min()),
        "q25": float(series.quantile(0.25)),
        "median": float(series.median()),
        "q75": float(series.quantile(0.75)),
        "max": float(series.max()),
    }


def build_subscribe_pie(df: pd.DataFrame) -> go.Figure:
    """Build a pie chart of subscribed vs. not subscribed."""
    overview = compute_overview(df)
    fig = px.pie(
        names=["Subscribed", "Not subscribed"],
        values=[overview["subscribed"], overview["not_subscribed"]],
        title="Subscription distribution",
        color_discrete_sequence=["#2ca02c", "#d62728"],
        hole=0.4,
    )
    fig.update_traces(textinfo="percent+label")
    return fig


def build_category_bar(df: pd.DataFrame, column: str) -> go.Figure:
    """Build a bar chart of record counts per category value."""
    data = compute_value_counts(df, column)
    fig = px.bar(
        data,
        x=column,
        y="count",
        title=f"Distribution of {column}",
        color="count",
        color_continuous_scale="Blues",
    )
    fig.update_layout(xaxis_title=column, yaxis_title="Count")
    return fig


def build_subscribe_rate_bar(df: pd.DataFrame, column: str) -> go.Figure:
    """Build a bar chart of subscription rate per category value."""
    data = compute_subscribe_rate_by_category(df, column)
    data = data.copy()
    data["rate_pct"] = data["rate"] * 100
    fig = px.bar(
        data,
        x=column,
        y="rate_pct",
        title=f"Subscription rate by {column}",
        color="rate_pct",
        color_continuous_scale="Greens",
    )
    fig.update_layout(xaxis_title=column, yaxis_title="Subscribe rate (%)")
    return fig


def build_age_histogram(df: pd.DataFrame) -> go.Figure:
    """Build a grouped bar chart of counts and subscribe rate per age group."""
    data = compute_age_groups(df)
    data = data.copy()
    data["rate_pct"] = data["rate"] * 100

    fig = go.Figure()
    fig.add_bar(x=data["age_group"], y=data["count"], name="Count", marker_color="#1f77b4")
    fig.add_scatter(
        x=data["age_group"],
        y=data["rate_pct"],
        name="Subscribe rate (%)",
        yaxis="y2",
        mode="lines+markers",
        line={"color": "#2ca02c"},
    )
    fig.update_layout(
        title="Age groups: count vs. subscribe rate",
        xaxis_title="Age group",
        yaxis={"title": "Count"},
        yaxis2={"title": "Subscribe rate (%)", "overlaying": "y", "side": "right"},
        legend={"orientation": "h", "y": 1.1},
    )
    return fig


def build_numeric_histogram(df: pd.DataFrame, column: str, nbins: int = 30) -> go.Figure:
    """Build a histogram of a numeric column colored by subscription status."""
    _require_column(df, column)
    _require_target(df)
    fig = px.histogram(
        df,
        x=column,
        color=TARGET_COLUMN,
        nbins=nbins,
        barmode="overlay",
        opacity=0.7,
        title=f"Distribution of {column} by subscription",
        color_discrete_map={"yes": "#2ca02c", "no": "#d62728"},
    )
    fig.update_layout(xaxis_title=column, yaxis_title="Count")
    return fig


def _require_column(df: pd.DataFrame, column: str) -> None:
    """Raise ValueError if ``column`` is absent from ``df``."""
    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")


def _require_target(df: pd.DataFrame) -> None:
    """Raise ValueError if the target column is absent from ``df``."""
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Target column not found: {TARGET_COLUMN}")
