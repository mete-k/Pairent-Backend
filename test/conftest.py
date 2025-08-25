import pytest
from src.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    # here, FORUM_SERVICE should be the real one (your create_app should set it up)
    with app.test_client() as client:
        yield client
