"""Streamlit page: interactive data analysis of the bank marketing dataset."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.models import visualizer
from app.models.data_loader import load_train_data

st.set_page_config(page_title="Data Analysis", page_icon="📊", layout="wide")


@st.cache_data(show_spinner=False)
def _get_data() -> pd.DataFrame:
    """Load training data once and cache it across reruns."""
    return load_train_data()


def render() -> None:
    """Render the data analysis page."""
    st.header("📊 Data Analysis")
    st.caption("Explore customer demographics and marketing effectiveness.")

    try:
        df = _get_data()
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"Failed to load data: {exc}")
        return

    _render_overview(df)
    st.divider()
    _render_subscribe_distribution(df)
    st.divider()
    _render_categorical_analysis(df)
    st.divider()
    _render_age_analysis(df)
    st.divider()
    _render_numeric_analysis(df)


def _render_overview(df: pd.DataFrame) -> None:
    overview = visualizer.compute_overview(df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total records", f"{overview['total_records']:,}")
    col2.metric("Features", overview["feature_count"])
    col3.metric("Subscribed", f"{overview['subscribed']:,}")
    col4.metric("Subscribe rate", f"{overview['subscribe_rate'] * 100:.2f}%")


def _render_subscribe_distribution(df: pd.DataFrame) -> None:
    st.subheader("Subscription distribution")
    st.plotly_chart(visualizer.build_subscribe_pie(df), use_container_width=True)


def _render_categorical_analysis(df: pd.DataFrame) -> None:
    st.subheader("Categorical feature analysis")
    column = st.selectbox(
        "Select a categorical feature",
        visualizer.CATEGORICAL_FEATURES,
        key="cat_feature",
    )
    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(visualizer.build_category_bar(df, column), use_container_width=True)
    with col_right:
        st.plotly_chart(visualizer.build_subscribe_rate_bar(df, column), use_container_width=True)


def _render_age_analysis(df: pd.DataFrame) -> None:
    st.subheader("Age group analysis")
    st.plotly_chart(visualizer.build_age_histogram(df), use_container_width=True)


def _render_numeric_analysis(df: pd.DataFrame) -> None:
    st.subheader("Numeric feature distribution")
    column = st.selectbox(
        "Select a numeric feature",
        visualizer.NUMERIC_FEATURES,
        key="num_feature",
    )
    nbins = st.slider("Number of bins", min_value=10, max_value=60, value=30, step=5)
    st.plotly_chart(
        visualizer.build_numeric_histogram(df, column, nbins=nbins),
        use_container_width=True,
    )
    summary = visualizer.compute_numeric_summary(df, column)
    st.dataframe(pd.DataFrame([summary]), use_container_width=True)


render()
