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
    """Main application entry point."""
    st.title("🏦 Bank Marketing Analysis & Prediction")

    st.sidebar.markdown("## Navigation")

    page = st.sidebar.radio(
        "Select Page",
        ["Home", "Data Analysis", "Prediction"],
    )

    if page == "Home":
        show_home()
    elif page == "Data Analysis":
        show_data_analysis()
    elif page == "Prediction":
        show_prediction()


def show_home() -> None:
    """Display home page."""
    st.markdown(
        """
        ## Welcome

        This system provides:

        - **Data Analysis**: Explore customer demographics and marketing effectiveness
        - **Prediction**: Predict customer subscription likelihood

        Select a page from the sidebar to begin.
        """
    )

    # Display data info
    data_dir = Path("data")
    if (data_dir / "train.csv").exists():
        import pandas as pd

        df = pd.read_csv(data_dir / "train.csv")
        st.metric("Total Records", len(df))
        st.metric("Columns", len(df.columns))


def show_data_analysis() -> None:
    """Display data analysis page."""
    st.header("📊 Data Analysis")
    st.info("Data analysis module will be implemented in US-3")


def show_prediction() -> None:
    """Display prediction page."""
    st.header("🔮 Prediction")
    st.info("Prediction module will be implemented in US-6")


if __name__ == "__main__":
    main()
