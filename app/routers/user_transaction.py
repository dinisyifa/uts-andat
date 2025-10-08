from sched import scheduler
import uuid
from typing import List
from fastapi import APIRouter, HTTPException, status
from app.models import CartAddItem, CartItemResponse, TransactionDetail

from app.routers.admin_film import list_film, list_studio
from app.routers.admin_jadwal import list_jadwal

# Simulasi "database" untuk transaksi dan keranjang, dimulai dari kosong
cart = []
transaction_history = []

router = APIRouter()

# ==========================================
# API - MANAJEMEN KERANJANG (USER)
# ==========================================

# CREATE - Tambah tiket ke keranjang
@router.post("/cart/add", tags=["User - Transaction"])
def add_ticket_to_cart(item: CartAddItem):
    # Cari jadwal dari list schedules berdasarkan schedule_id dari input
    schedule_found = next((s for s in scheduler if s.get("id") == item.schedule_id), None)
    if not schedule_found:
        raise HTTPException(status_code=404, detail=f"Jadwal dengan ID '{item.schedule_id}' tidak ditemukan.")

    # Cek apakah kursi ada dan tersedia di jadwal yang ditemukan
    # Asumsi: struktur seats adalah dictionary -> {"A1": {"available": True}, ...}
    seat = schedule_found["seats"].get(item.seat_number)
    if not seat:
        raise HTTPException(status_code=404, detail=f"Kursi '{item.seat_number}' tidak ditemukan di jadwal ini.")
    if not seat["available"]:
        raise HTTPException(status_code=400, detail=f"Kursi '{item.seat_number}' sudah tidak tersedia.")

    # Cek apakah item yang sama persis sudah ada di keranjang
    for cart_item in cart:
        if cart_item["schedule_id"] == item.schedule_id and cart_item["seat_number"] == item.seat_number:
            raise HTTPException(status_code=400, detail=f"Tiket untuk kursi '{item.seat_number}' di jadwal ini sudah ada di keranjang.")

    # Cari detail film dari list_film berdasarkan movie_id yang ada di jadwal
    movie_found = next((f for f in list_film if f.get("id") == schedule_found["movie_id"]), None)
    if not movie_found:
        raise HTTPException(status_code=404, detail="Film untuk jadwal ini tidak ditemukan di daftar film.")

    # Buat item keranjang baru
    new_cart_item = {
        "item_id": f"ITEM-{uuid.uuid4().hex[:6].upper()}",
        "schedule_id": schedule_found["id"],
        "movie_id": movie_found["id"],
        "movie_title": movie_found["title"],
        "schedule": f"{schedule_found['date']} {schedule_found['time']}",
        "studio": schedule_found["studio"],
        "seat_number": item.seat_number,
        "price": movie_found["price"]
    }
    cart.append(new_cart_item)
    return {"message": "Tiket berhasil ditambahkan ke keranjang", "data": new_cart_item}


# READ - Lihat isi keranjang
@router.get("/cart", tags=["User - Transaction"])
def view_cart():
    if not cart:
        # Meskipun keranjang kosong bukan error, konsistensi respons bisa dijaga
        return {"message": "Keranjang belanja saat ini kosong.", "data": []}
    return {"message": "Isi keranjang berhasil diambil", "data": cart}


# DELETE - Hapus item dari keranjang
@router.delete("/cart/remove/{item_id}", status_code=status.HTTP_200_OK, tags=["User - Transaction"])
def remove_ticket_from_cart(item_id: str):
    global cart
    for idx, item in enumerate(cart):
        if item["item_id"] == item_id:
            del cart[idx]
            return {"message": f"Item dengan ID {item_id} berhasil dihapus dari keranjang"}
    raise HTTPException(status_code=404, detail=f"Item dengan ID '{item_id}' tidak ditemukan di keranjang.")


# ==========================================
# API - PROSES CHECKOUT (USER)
# ==========================================

@router.post("/checkout", tags=["User - Transaction"])
def checkout():
    if not cart:
        raise HTTPException(status_code=400, detail="Keranjang belanja kosong, tidak bisa checkout.")

    total_price = 0
    booked_tickets = []

    # Validasi ulang semua kursi sebelum finalisasi
    for item in cart:
        schedule = next((s for s in schedule if s.get("id") == item["schedule_id"]), None)
        if not schedule or not schedule["seats"].get(item["seat_number"], {}).get("available"):
            raise HTTPException(
                status_code=400,
                detail=f"Checkout gagal. Kursi '{item['seat_number']}' untuk film '{item['movie_title']}' sudah tidak tersedia lagi."
            )
        total_price += item["price"]

    # Proses checkout setelah semua valid
    for item in cart:
        # 1. Ubah status kursi menjadi "booked" (tidak tersedia) di data utama
        schedule = next((s for s in schedule if s.get("id") == item["schedule_id"]), None)
        if schedule:
            schedule["seats"][item["seat_number"]]["available"] = False
        
        # 2. Salin item ke daftar tiket yang akan di-checkout
        booked_tickets.append(item)

    # 3. Hasilkan kode booking
    booking_code = f"BK-{uuid.uuid4().hex[:8].upper()}"

    # 4. Buat data transaksi
    new_transaction = {
        "booking_code": booking_code,
        "total_price": total_price,
        "tickets": booked_tickets
    }

    # 5. Simpan ke riwayat transaksi
    transaction_history.append(new_transaction)

    # 6. Kosongkan keranjang
    cart.clear()

    return {"message": "Checkout berhasil", "data": new_transaction}