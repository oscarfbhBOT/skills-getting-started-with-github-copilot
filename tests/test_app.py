from fastapi.testclient import TestClient
from src.app import app, activities


client = TestClient(app)


def test_unregister_success():
    # Ensure participant exists for test
    activity = "Chess Club"
    email = "daniel@mergington.edu"
    assert email in activities[activity]["participants"]

    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 200
    data = resp.json()
    assert "Se ha dado de baja a" in data.get("message", "")
    # Participant should no longer be in list
    assert email not in activities[activity]["participants"]


def test_unregister_not_registered():
    activity = "Chess Club"
    email = "nonexistent@mergington.edu"
    # ensure not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 404
    data = resp.json()
    assert data.get("detail") == "El estudiante no está inscrito en esta actividad"


def test_unregister_activity_not_found():
    activity = "Actividad Inexistente"
    email = "someone@mergington.edu"
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 404
    data = resp.json()
    assert data.get("detail") == "Actividad no encontrada"
