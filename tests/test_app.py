"""
Pytest-based tests for the FastAPI extracurricular activities API.

Tests cover:
- GET /activities endpoint
- POST signup success and error cases
- DELETE unregister success and error cases
- Proper isolation of in-memory activity state between tests

Run tests with: pytest
"""

import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
initial_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before and after each test."""
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))
    yield


def test_get_activities():
    """Test GET /activities returns all activities with correct structure."""
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(data["Chess Club"]["participants"], list)
    assert len(data["Chess Club"]["participants"]) == 2


def test_signup_for_activity_success():
    """Test successful signup for an activity."""
    email = "alex@mergington.edu"
    activity = quote("Chess Club", safe="")

    response = client.post(f"/activities/{activity}/signup?email={quote(email, safe='')}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    """Test that duplicate signup is rejected with 400 status."""
    email = "michael@mergington.edu"
    activity = quote("Chess Club", safe="")

    response = client.post(f"/activities/{activity}/signup?email={quote(email, safe='')}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_invalid_activity_returns_404():
    """Test that signup to non-existent activity returns 404."""
    email = "alex@mergington.edu"
    activity = quote("Nonexistent Activity", safe="")

    response = client.post(f"/activities/{activity}/signup?email={quote(email, safe='')}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_success():
    """Test successful unregistration from an activity."""
    email = "michael@mergington.edu"
    activity = quote("Chess Club", safe="")

    response = client.delete(f"/activities/{activity}/unregister?email={quote(email, safe='')}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_non_registered_student_returns_400():
    """Test that unregister for non-registered student returns 400."""
    email = "notregistered@mergington.edu"
    activity = quote("Chess Club", safe="")

    response = client.delete(f"/activities/{activity}/unregister?email={quote(email, safe='')}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_invalid_activity_returns_404():
    """Test that unregister from non-existent activity returns 404."""
    email = "michael@mergington.edu"
    activity = quote("Nonexistent Activity", safe="")

    response = client.delete(f"/activities/{activity}/unregister?email={quote(email, safe='')}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
