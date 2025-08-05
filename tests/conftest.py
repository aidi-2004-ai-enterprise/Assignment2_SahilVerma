import pytest
from app.main import load_model_and_metadata

@pytest.fixture(scope="session", autouse=True)
def load_model():
    """Load model and metadata once for all tests"""
    load_model_and_metadata()