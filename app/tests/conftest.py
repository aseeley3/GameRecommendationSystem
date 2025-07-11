import pytest
from app import create_app

@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for testing."""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    return app

@pytest.fixture(scope="session")
def client(app):
    """A test client for the app."""
    return app.test_client() 