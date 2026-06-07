"""Basic health tests."""

import pytest


def test_python_version():
    """Verify Python version is 3.11+."""
    import sys

    major, minor = sys.version_info[:2]
    assert major == 3 and minor >= 11, f"Python 3.11+ required, got {major}.{minor}"


def test_app_imports():
    """Verify app modules can be imported."""
    import app
    import app.models
    import app.pages
    import app.utils

    assert app.__version__ is not None


def test_data_files_exist():
    """Verify data files exist."""
    from pathlib import Path

    data_dir = Path(__file__).parent.parent / "data"
    assert (data_dir / "train.csv").exists()
    assert (data_dir / "test.csv").exists()


@pytest.mark.unit
def test_placeholder():
    """Placeholder test to verify pytest runs."""
    assert True
