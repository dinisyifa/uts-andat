from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_tambah_film():
    film_baru = {
        "id": "F001",
        "title": "Avengers Endgame",
        "genre": "Action",
        "duration": 200 "menit",
        "price": 40000
    }
    response = client.post("/movies", json=film_baru)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Film berhasil ditambahkan"
    assert data["data"]["title"] == "Avengers: Endgame"

def test_tambah_film_duplikat():
    film_duplikat = {
        "id": "F001",
        "title": "Meow Wars",
        "genre": "Action",
        "duration": 120,
        "price": 40000
    }
    response = client.post("/movies", json=film_duplikat)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "ID film sudah ada"

def test_lihat_semua_film():
    response = client.get("/movies")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Daftar semua film berhasil diambil"
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0

def test_lihat_detail_film():
    response = client.get("/movies/F001")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Detail film ditemukan"
    assert data["data"]["id"] == "F001"

def test_perbarui_film():
    film_update = {
        "id": "F001",
        "title": "Meow Wars: The Return",
        "genre": "Sci-Fi",
        "duration": 130,
        "price": 55000
    }
    response = client.put("/movies/F001", json=film_update)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Data film berhasil diperbarui"
    assert data["data"]["title"] == "Meow Wars: The Return"

def test_hapus_film():
    response = client.delete("/movies/F001")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Film dengan ID F001 berhasil dihapus"

def test_lihat_setelah_hapus():
    response = client.get("/movies/F001")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Film tidak ditemukan"