from fastapi.testclient import TestClient
from main import app  # ganti sesuai nama file FastAPI utama kamu

client = TestClient(app)

# --- TEST KATALOG KURSI ---

def test_get_seat_catalog():
    # pastikan jadwal dengan id=1 sudah ada di sistem
    response = client.get("/schedules/1/seats")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert "seat_number" in data[0]
    assert "is_available" in data[0]

# --- TEST PEMILIHAN KURSI ---

def test_select_seats():
    # user memilih kursi A1, A2
    response = client.post(
        "/schedules/1/select-seats",
        json={"user_name": "Carens", "selected_seats": ["A1", "A2"]}
    )
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()

    # pastikan kursi yang dipilih dikonfirmasi
    assert data["message"] == "Seats selected successfully"
    assert set(data["selected_seats"]) == {"A1", "A2"}

def test_seat_availability_after_selection():
    # pastikan kursi A1 dan A2 sekarang tidak tersedia
    response = client.get("/schedules/1/seats")
    assert response.status_code == 200
    seats = response.json()

    # cari kursi A1 dan A2 di daftar
    unavailable = [s for s in seats if s["seat_number"] in ["A1", "A2"]]
    assert all(not s["is_available"] for s in unavailable)

# --- OPSIONAL: TEST BATALKAN PILIHAN KURSI ---

def test_release_seats():
    response = client.post(
        "/schedules/1/release-seats",
        json={"user_name": "Carens", "released_seats": ["A1"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Seats released successfully"

    # cek ulang kursi A1 jadi available lagi
    response = client.get("/schedules/1/seats")
    seats = response.json()
    seat_a1 = next((s for s in seats if s["seat_number"] == "A1"), None)
    assert seat_a1 and seat_a1["is_available"]