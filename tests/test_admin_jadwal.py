import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routers import admin_jadwal
from app.routers.admin_film import list_film, list_studio

# Siapkan FastAPI app sementara untuk testing
app = FastAPI()
app.include_router(admin_jadwal.router)
client = TestClient(app)

# Setup dummy data untuk film dan studio
@pytest.fixture(autouse=True)
def setup_dummy_data():
    list_film.clear()
    list_studio.clear()
    admin_jadwal.list_jadwal.clear()
    admin_jadwal.schedule_counter = 1

    list_film.append({
        "id": "f1",
        "title": "Inception"
    })

    list_studio.append({
        "id_studio": "s1",
        "nama_studio": "Studio 1"
    })


# ======================================================
# TEST 1 - Tambah jadwal baru (POST)
# ======================================================
def test_tambah_jadwal_berhasil():
    response = client.post(
        "/schedules",
        params={
            "movie_id": "f1",
            "studio_id": "s1",
            "date": "2025-10-10",
            "time": "19:00"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Jadwal berhasil dibuat"
    assert data["data"]["movie_title"] == "Inception"
    assert data["data"]["studio_id"] == "s1"
    assert len(data["data"]["seats"]) == 8  # 8 baris kursi


# ======================================================
# TEST 2 - Gagal tambah jadwal (film tidak ditemukan)
# ======================================================
def test_tambah_jadwal_gagal_film_tidak_ada():
    response = client.post(
        "/schedules",
        params={
            "movie_id": "f999",
            "studio_id": "s1",
            "date": "2025-10-10",
            "time": "19:00"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Film tidak ditemukan"


# ======================================================
# TEST 3 - Gagal tambah jadwal (studio tidak ditemukan)
# ======================================================
def test_tambah_jadwal_gagal_studio_tidak_ada():
    response = client.post(
        "/schedules",
        params={
            "movie_id": "f1",
            "studio_id": "s999",
            "date": "2025-10-10",
            "time": "19:00"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Studio tidak ditemukan"


# ======================================================
# TEST 4 - Lihat semua jadwal (GET)
# ======================================================
def test_lihat_semua_jadwal():
    # Tambah dulu satu jadwal
    client.post("/schedules", params={
        "movie_id": "f1", "studio_id": "s1", "date": "2025-10-10", "time": "19:00"
    })

    response = client.get("/schedules")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Daftar semua jadwal berhasil diambil"
    assert len(data["data"]) == 1


# ======================================================
# TEST 5 - Lihat semua jadwal (belum ada)
# ======================================================
def test_lihat_semua_jadwal_kosong():
    response = client.get("/schedules")
    assert response.status_code == 404
    assert response.json()["detail"] == "Belum ada jadwal yang terdaftar"


# ======================================================
# TEST 6 - Lihat jadwal berdasarkan film
# ======================================================
def test_lihat_jadwal_film():
    # Tambah dulu jadwal
    client.post("/schedules", params={
        "movie_id": "f1", "studio_id": "s1", "date": "2025-10-10", "time": "19:00"
    })

    response = client.get("/movies/f1/schedules")
    assert response.status_code == 200
    data = response.json()
    assert "Jadwal untuk film f1 ditemukan" in data["message"]
    assert data["data"][0]["movie_id"] == "f1"


# ======================================================
# TEST 7 - Lihat jadwal film yang belum ada
# ======================================================
def test_lihat_jadwal_film_tidak_ada():
    response = client.get("/movies/f999/schedules")
    assert response.status_code == 404
    assert response.json()["detail"] == "Belum ada jadwal untuk film ini"