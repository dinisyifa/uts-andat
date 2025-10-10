import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routers import user_transaction
from app.routers.admin_film import list_film
from app.routers.admin_jadwal import list_jadwal

app = FastAPI()
app.include_router(user_transaction.router)
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_data():
    """Reset semua variabel global sebelum tiap test"""
    list_film.clear()
    list_jadwal.clear()
    user_transaction.cart.clear()
    user_transaction.transaction_history.clear()

    # Setup dummy film dan jadwal
    list_film.append({
        "id": "f1",
        "title": "Interstellar",
        "price": 75000
    })
    list_jadwal.append({
        "id": "sch1",
        "movie_id": "f1",
        "studio": "Studio 2",
        "date": "2025-10-11",
        "time": "20:00",
        "seats": {"A1": {"available": True}, "A2": {"available": True}}
    })


# ================================================================
# TEST 1 - Tambah ke cart
# ================================================================
def test_add_ticket_success():
    payload = {"schedule_id": "sch1", "seat_number": "A1"}
    res = client.post("/cart/add", json=payload)
    assert res.status_code == 200
    assert res.json()["message"] == "Tiket berhasil ditambahkan ke keranjang"


def test_add_ticket_fail_schedule_not_found():
    payload = {"schedule_id": "unknown", "seat_number": "A1"}
    res = client.post("/cart/add", json=payload)
    assert res.status_code == 404
    assert "tidak ditemukan" in res.json()["detail"]


def test_add_ticket_fail_seat_not_found():
    payload = {"schedule_id": "sch1", "seat_number": "Z9"}
    res = client.post("/cart/add", json=payload)
    assert res.status_code == 404
    assert "tidak ditemukan" in res.json()["detail"]


# ================================================================
# TEST 2 - View dan Remove cart
# ================================================================
def test_view_and_remove_cart():
    # Tambahkan item ke cart
    client.post("/cart/add", json={"schedule_id": "sch1", "seat_number": "A1"})
    res_view = client.get("/cart")
    assert res_view.status_code == 200
    assert len(res_view.json()["data"]) == 1

    item_id = res_view.json()["data"][0]["item_id"]
    res_remove = client.delete(f"/cart/remove/{item_id}")
    assert res_remove.status_code == 200
    assert "berhasil dihapus" in res_remove.json()["message"]

    res_empty = client.get("/cart")
    assert res_empty.json()["data"] == []


# ================================================================
# TEST 3 - Checkout
# ================================================================
def test_checkout_success():
    client.post("/cart/add", json={"schedule_id": "sch1", "seat_number": "A1"})
    res_checkout = client.post("/checkout")
    assert res_checkout.status_code == 200
    data = res_checkout.json()["data"]
    assert data["booking_code"].startswith("BK-")
    assert len(data["tickets"]) == 1
    assert user_transaction.cart == []  # cart dikosongkan


def test_checkout_empty_cart():
    res_checkout = client.post("/checkout")
    assert res_checkout.status_code == 400
    assert res_checkout.json()["detail"] == "Keranjang belanja kosong, tidak bisa checkout."
