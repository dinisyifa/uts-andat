import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime, timedelta
from app.routers import user_catalog
from app.routers.admin_film import list_film
from app.routers.admin_jadwal import list_jadwal

# Setup aplikasi sementara untuk uji
app = FastAPI()
app.include_router(user_catalog.router)
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_dummy_data():
    """Reset semua data sebelum tiap test"""
    list_film.clear()
    list_jadwal.clear()
    user_catalog.SEATS_BY_SCHEDULE.clear()
    user_catalog.HOLDS.clear()

    # Tambahkan 1 film dan 1 jadwal
    list_film.append({
        "id": "f1",
        "title": "Inception",
        "duration": 120,
        "price": 50000,
        "synopsis": "A mind-bending thriller."
    })
    list_jadwal.append({
        "id_jadwal": "sch1",
        "movie_id": "f1",
        "movie_title": "Inception",
        "studio_name": "Studio 1",
        "date": "2025-10-10",
        "time": "19:00"
    })


# ================================================================
# TEST 1 - now_playing()
# ================================================================
def test_now_playing_success():
    res = client.get("/now_playing")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 1
    assert data["movies"][0]["title"] == "Inception"


def test_now_playing_no_movies():
    list_film.clear()
    res = client.get("/now_playing")
    assert res.status_code == 404
    assert res.json()["detail"] == "Belum ada film"


# ================================================================
# TEST 2 - user_movies()
# ================================================================
def test_user_movies():
    res = client.get("/movies")
    assert res.status_code == 200
    data = res.json()
    assert len(data["movies"]) == 1
    assert data["movies"][0]["title"] == "Inception"
    assert len(data["movies"][0]["showtimes"]) == 1


# ================================================================
# TEST 3 - movie_details()
# ================================================================
def test_movie_details_success():
    res = client.get("/movies/f1/details")
    assert res.status_code == 200
    data = res.json()
    assert data["movie"]["title"] == "Inception"
    assert len(data["showtimes"]) == 1
    assert "seat_summary" in data


def test_movie_details_not_found():
    res = client.get("/movies/f999/details")
    assert res.status_code == 404
    assert res.json()["detail"] == "Film tidak ditemukan"


# ================================================================
# TEST 4 - seat_map
# ================================================================
def test_seat_map_success():
    res = client.get("/schedules/sch1/seats")
    assert res.status_code == 200
    data = res.json()
    assert data["rows"] == 8
    assert data["cols"] == 12
    assert "display" in data


def test_seat_map_not_found():
    res = client.get("/schedules/unknown/seats")
    assert res.status_code == 200  # Auto init seats
    assert "seats" in res.json()


# ================================================================
# TEST 5 - hold, confirm, release kursi
# ================================================================
def test_hold_confirm_release_cycle():
    # HOLD kursi
    res_hold = client.post("/schedules/sch1/hold", params={"seats": "A1,A2"})
    assert res_hold.status_code == 200
    held = res_hold.json()["held"]
    assert "A1" in held

    # CONFIRM kursi
    res_confirm = client.post("/schedules/sch1/confirm", params={"seats": "A1"})
    assert res_confirm.status_code == 200
    sold = res_confirm.json()["sold"]
    assert "A1" in sold

    # RELEASE kursi (A2 yang masih hold)
    res_release = client.post("/schedules/sch1/release", params={"seats": "A2"})
    assert res_release.status_code == 200
    released = res_release.json()["released"]
    assert "A2" in released