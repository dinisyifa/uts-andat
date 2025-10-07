from fastapi.testclient import TestClient
from main import app  # pastikan nama file utama FastAPI kamu adalah main.py

client = TestClient(app)

# --- TEST MOVIE ENDPOINTS ---

def test_add_movie():
    response = client.post(
        "/movies",
        json={"id": 1, "title": "Meow Wars", "genre": "Action", "duration": 120, "price": 50000},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Meow Wars"

def test_get_movies():
    response = client.get("/movies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(movie["title"] == "Meow Wars" for movie in data)

def test_get_movie_by_id():
    response = client.get("/movies/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Meow Wars"

def test_delete_movie():
    response = client.delete("/movies/1")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Movie deleted successfully"

# --- TEST BOOKING ENDPOINTS ---

def test_create_booking():
    # pastikan film id 2 sudah ada di data dummy API
    response = client.post(
        "/bookings",
        json={"movie_id": 2, "user_name": "Carens", "seats": [1, 2, 3]},
    )
    assert response.status_code == 201
    data = response.json()
    assert "booking_code" in data
    assert data["user_name"] == "Carens"

def test_get_bookings():
    response = client.get("/bookings")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)