from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture
def reset_activities():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original))


def test_get_activities_returns_activity_catalog(reset_activities):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_for_activity_registers_student(reset_activities):
    activity_name = "Science Club"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    payload = client.get("/activities").json()
    assert email in payload[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicate_registration(reset_activities):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_delete_participant_removes_email_from_activity(reset_activities):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}

    activities_payload = client.get("/activities").json()
    assert email not in activities_payload[activity_name]["participants"]


def test_missing_activity_returns_404(reset_activities):
    response = client.post("/activities/Unknown%20Club/signup?email=test@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_without_email_returns_422(reset_activities):
    response = client.post("/activities/Science%20Club/signup")

    assert response.status_code == 422


def test_delete_missing_activity_returns_404(reset_activities):
    response = client.delete("/activities/Unknown%20Club/participants/test@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_missing_participant_returns_404(reset_activities):
    activity_name = "Chess Club"
    email = "not-registered@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
