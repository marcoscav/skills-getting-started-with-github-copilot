import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield


def test_get_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_and_duplicate():
    activity = "Chess Club"
    email = "testuser@mergington.edu"

    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"

    duplicate_response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant():
    activity = "Programming Class"
    email = "removeuser@mergington.edu"

    signup_response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert signup_response.status_code == 200

    delete_response = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Removed {email} from {activity}"

    missing_response = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Participant not found"


def test_activity_not_found():
    response = client.post("/activities/Unknown/signup", params={"email": "hello@mergington.edu"})
    assert response.status_code == 404

    delete_response = client.delete("/activities/Unknown/participants", params={"email": "hello@mergington.edu"})
    assert delete_response.status_code == 404
