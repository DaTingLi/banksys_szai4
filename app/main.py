"""Bank marketing analysis and prediction system.

Main entry point for Streamlit application.
"""

from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Bank Marketing System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    """Render the home / landing page.

    Navigation between pages is handled by Streamlit's native multipage
    mechanism (files under ``app/pages/``), so this entry point only shows
    the landing content and a dataset snapshot.
    """
    st.title("🏦 Bank Marketing Analysis & Prediction")

    st.markdown(
        """
        ## Welcome

        This system provides:

        - **Data Analysis**: Explore customer demographics and marketing effectiveness
        - **Prediction**: Predict customer subscription likelihood

        Use the sidebar to navigate between pages.
        """
    )

    data_path = Path("data") / "train.csv"
    if data_path.exists():
        import pandas as pd

        df = pd.read_csv(data_path)
        col1, col2 = st.columns(2)
        col1.metric("Total Records", f"{len(df):,}")
        col2.metric("Columns", len(df.columns))


if __name__ == "__main__":
    main()
