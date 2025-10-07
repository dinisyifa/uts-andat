from fastapi.testclient import TestClient
from main import app  # pastikan file utama FastAPI kamu bernama main.py

client = TestClient(app)

def test_add_schedule():
    # misal film dengan id 1 sudah ada
    response = client.post(
        "/schedules",
        json={
            "id": 1,
            "movie_id": 1,
            "date": "2025-10-15",
            "time": "19:30",
            "studio": "Studio 1",
            "available_seats": 50
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["movie_id"] == 1
    assert data["studio"] == "Studio 1"

def test_get_all_schedules():
    response = client.get("/schedules")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "date" in data[0]

def test_get_schedule_by_id():
    response = client.get("/schedules/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["studio"] == "Studio 1"

def test_delete_schedule():
    response = client.delete("/schedules/1")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Schedule deleted successfully"