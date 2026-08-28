"""Pytest fixtures for activity API tests using AAA pattern."""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Arrange: Provide a test client for API calls.
    
    This fixture creates a TestClient instance that can be used to make
    requests to the FastAPI application without running a live server.
    """
    return TestClient(app)


@pytest.fixture
def fresh_activities(monkeypatch):
    """
    Arrange: Reset activities to a known clean state for each test.
    
    This fixture ensures test isolation by providing a fresh copy of activities
    with predictable data (smaller participant lists and capacities for easier testing).
    Uses monkeypatch to replace the app's activities dict during the test.
    """
    test_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["alice@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 3,
            "participants": []
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 2,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    monkeypatch.setattr("src.app.activities", test_activities)
    return test_activities
