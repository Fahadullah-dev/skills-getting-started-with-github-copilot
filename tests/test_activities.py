import copy
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def setup_function(function):
    # Save a deep copy of activities to restore after each test
    function._activities_backup = copy.deepcopy(activities)


def teardown_function(function):
    # Restore activities state
    activities.clear()
    activities.update(function._activities_backup)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    # Check a known activity
    assert "Chess Club" in data


def test_signup_and_get_participant():
    email = "test.student@mergington.edu"
    activity = "Programming Class"

    # Ensure not already registered
    assert email not in activities[activity]["participants"]

    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # Verify participant is listed
    r2 = client.get("/activities")
    assert r2.status_code == 200
    data = r2.json()
    assert email in data[activity]["participants"]


def test_signup_duplicate_fails():
    email = "duplicate@mergington.edu"
    activity = "Gym Class"

    # First signup
    r1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r1.status_code == 200

    # Second should fail with 400
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400


def test_unregister_success_and_failure():
    # Use existing participant in Chess Club
    activity = "Chess Club"
    email = "michael@mergington.edu"

    assert email in activities[activity]["participants"]

    r = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r.status_code == 200
    assert "Removed" in r.json().get("message", "")

    # Removing again should fail
    r2 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r2.status_code == 400


def test_signup_invalid_activity():
    r = client.post("/activities/NoSuchActivity/signup?email=someone@x.com")
    assert r.status_code == 404


def test_unregister_invalid_activity():
    r = client.post("/activities/NoSuchActivity/unregister?email=someone@x.com")
    assert r.status_code == 404
