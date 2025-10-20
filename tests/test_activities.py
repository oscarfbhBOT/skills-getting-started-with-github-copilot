from fastapi.testclient import TestClient
from src.app import app, activities


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Check a known activity exists
    assert "Chess Club" in data


def test_signup_success_and_duplicate():
    activity = "Programming Class"
    email = "testuser@example.com"

    # Ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup should succeed
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    data = resp.json()
    assert "Se ha inscrito" in data.get("message", "")
    assert email in activities[activity]["participants"]

    # Duplicate signup should return 400
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400
    data2 = resp2.json()
    assert data2.get("detail") == "El estudiante ya está inscrito"

    # Clean up
    activities[activity]["participants"].remove(email)


def test_signup_capacity_full():
    # Create a temporary activity with capacity 1
    temp_name = "Temp Small"
    activities[temp_name] = {
        "description": "Temp",
        "schedule": "Now",
        "max_participants": 1,
        "participants": []
    }

    email1 = "first@example.com"
    email2 = "second@example.com"

    # First signup ok
    r1 = client.post(f"/activities/{temp_name}/signup", params={"email": email1})
    assert r1.status_code == 200

    # Second should fail (full)
    r2 = client.post(f"/activities/{temp_name}/signup", params={"email": email2})
    assert r2.status_code == 400
    assert r2.json().get("detail") == "La actividad está llena"

    # Clean up
    activities.pop(temp_name, None)
