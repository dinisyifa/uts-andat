from fastapi.testclient import TestClient
from main import app  # pastikan di main.py kamu sudah include router user_transaction

client = TestClient(app)

def test_add_to_cart():
    response = client.post(
        "/cart/add",
        params={
            "username": "carens",
            "movie_id": 1,
            "schedule_id": 10,
            "seats": ["A1", "A2"],
            "price_per_seat": 50000
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Item added to cart"
    assert len(data["cart"]) > 0
    assert data["cart"][0]["total_price"] == 100000

def test_get_cart():
    response = client.get("/cart/carens")
    assert response.status_code == 200
    data = response.json()
    assert "cart" in data
    assert data["username"] == "carens"

def test_remove_from_cart():
    response = client.delete(
        "/cart/remove",
        params={"username": "carens", "movie_id": 1}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Item removed from cart"

def test_add_multiple_and_checkout():
    # Tambahkan lagi item baru
    client.post(
        "/cart/add",
        params={
            "username": "carens",
            "movie_id": 2,
            "schedule_id": 12,
            "seats": ["B1", "B2", "B3"],
            "price_per_seat": 45000
        }
    )
    # Checkout
    response = client.post("/cart/checkout", params={"username": "carens"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Checkout successful"
    assert "transaction" in data
    assert data["transaction"]["total_amount"] == 135000
    assert "BOOK" in data["transaction"]["booking_code"]

def test_empty_cart_after_checkout():
    response = client.get("/cart/carens")
    assert response.status_code == 404  # karena keranjang sudah kosong