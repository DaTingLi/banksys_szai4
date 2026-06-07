"""Streamlit page: online subscription prediction via a point-and-click form."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.models.data_loader import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    load_train_data,
)
from app.models.predictor import ModelNotFoundError, predict

st.set_page_config(page_title="Prediction", page_icon="🔮", layout="wide")

# Friendly labels and sensible slider config per numeric feature.
# (min, max, default, step) — ranges derived from the training data.
NUMERIC_CONFIG = {
    "age": (16, 101, 38, 1),
    "duration": (0, 5149, 353, 1),
    "campaign": (0, 57, 1, 1),
    "pdays": (0, 1048, 964, 1),
    "previous": (0, 6, 0, 1),
    "emp_var_rate": (-3.4, 1.4, 1.1, 0.1),
    "cons_price_index": (87.6, 99.5, 93.5, 0.1),
    "cons_conf_index": (-53.3, -25.5, -40.6, 0.1),
    "lending_rate3m": (0.6, 5.3, 3.9, 0.1),
    "nr_employed": (4715.0, 5489.5, 5134.0, 1.0),
}


@st.cache_data(show_spinner=False)
def _category_options() -> dict[str, list[str]]:
    """Derive selectbox options for each categorical feature from the data."""
    df = load_train_data()
    return {col: sorted(df[col].dropna().unique().tolist()) for col in CATEGORICAL_FEATURES}


def _collect_inputs(options: dict[str, list[str]]) -> dict:
    """Render form widgets and collect the feature values into a dict."""
    features: dict = {}

    st.markdown("#### Customer profile")
    cols = st.columns(3)
    for idx, feature in enumerate(CATEGORICAL_FEATURES):
        with cols[idx % 3]:
            features[feature] = st.selectbox(feature, options[feature], key=f"in_{feature}")

    st.markdown("#### Numeric indicators")
    num_cols = st.columns(2)
    for idx, feature in enumerate(NUMERIC_FEATURES):
        low, high, default, step = NUMERIC_CONFIG[feature]
        with num_cols[idx % 2]:
            features[feature] = st.slider(
                feature,
                min_value=float(low),
                max_value=float(high),
                value=float(default),
                step=float(step),
                key=f"in_{feature}",
            )
    return features


def _render_result(result: dict) -> None:
    """Display prediction label, probability gauge, and an advisory message."""
    probability = result["probability"]
    subscribe = result["subscribe"]
    confidence = result["confidence"]

    col1, col2 = st.columns([1, 2])
    with col1:
        if subscribe:
            st.success("✅ Likely to SUBSCRIBE")
        else:
            st.error("❌ Unlikely to subscribe")
        st.metric("Confidence", confidence.upper())

    with col2:
        st.markdown(f"**Subscription probability: {probability * 100:.1f}%**")
        st.progress(probability)

    if subscribe:
        st.info("Recommendation: prioritise this lead for follow-up contact.")
    else:
        st.info("Recommendation: lower priority; consider nurturing before contact.")


def render() -> None:
    """Render the prediction page."""
    st.header("🔮 Subscription Prediction")
    st.caption("Fill in the customer profile and predict the subscription likelihood.")

    try:
        options = _category_options()
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"Failed to load data for form options: {exc}")
        return

    with st.form("prediction_form"):
        features = _collect_inputs(options)
        submitted = st.form_submit_button("Predict", type="primary")

    if not submitted:
        return

    try:
        result = predict(features)
    except ModelNotFoundError:
        st.warning(
            "Model not found. Train it first with `python -m app.ml.train`, "
            "then reload this page."
        )
        return
    except ValueError as exc:
        st.error(f"Invalid input: {exc}")
        return

    st.divider()
    _render_result(result)
    with st.expander("Submitted features"):
        st.dataframe(pd.DataFrame([features]), use_container_width=True)


render()
