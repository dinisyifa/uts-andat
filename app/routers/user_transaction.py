# file: app/routers/user_transaction.py

import uuid
from typing import List
from fastapi import APIRouter, HTTPException, status
from app.models import CartAddItem, CartItemResponse, TransactionDetail

# --- Impor Data dari Modul Admin ---
# Kita asumsikan data ini adalah list of dictionaries
from app.routers.admin_film import list_film
from app.routers.admin_jadwal import list_jadwal

# --- Variabel Lokal untuk Modul Ini ---
cart = []
transaction_history = []

router = APIRouter()

# ==========================================
# API - MANAJEMEN KERANJANGB (USER)
# ==========================================

@router.post("/cart/add", tags=["User - Transaction"])
def add_ticket_to_cart(item: CartAddItem):
    # 1. Perbaikan: Cari di 'list_jadwal' bukan 'scheduler'
    schedule_found = next((s for s in list_jadwal if s.get("id") == item.schedule_id), None)
    if not schedule_found:
        raise HTTPException(status_code=404, detail=f"Jadwal dengan ID '{item.schedule_id}' tidak ditemukan.")

    # Cek ketersediaan kursi
    seat = schedule_found.get("seats", {}).get(item.seat_number)
    if not seat:
        raise HTTPException(status_code=404, detail=f"Kursi '{item.seat_number}' tidak ditemukan di jadwal ini.")
    if not seat.get("available"):
        raise HTTPException(status_code=400, detail=f"Kursi '{item.seat_number}' sudah tidak tersedia.")

    # Cek duplikat di keranjang
    for cart_item in cart:
        if cart_item["schedule_id"] == item.schedule_id and cart_item["seat_number"] == item.seat_number:
            raise HTTPException(status_code=400, detail=f"Tiket untuk kursi '{item.seat_number}' di jadwal ini sudah ada di keranjang.")

    # Cari detail film
    movie_found = next((f for f in list_film if f.get("id") == schedule_found.get("movie_id")), None)
    if not movie_found:
        raise HTTPException(status_code=404, detail="Film untuk jadwal ini tidak ditemukan.")

    # Buat item keranjang baru dengan aman
    new_cart_item = {
        "item_id": f"ITEM-{uuid.uuid4().hex[:6].upper()}",
        "schedule_id": schedule_found.get("id"),
        "movie_id": movie_found.get("id"),
        "movie_title": movie_found.get("title"),
        "schedule": f"{schedule_found.get('date', '')} {schedule_found.get('time', '')}",
        "studio": schedule_found.get("studio", "N/A"),
        "seat_number": item.seat_number,
        "price": movie_found.get("price")
    }
    cart.append(new_cart_item)
    return {"message": "Tiket berhasil ditambahkan ke keranjang", "data": new_cart_item}


@router.get("/cart", tags=["User - Transaction"])
def view_cart():
    if not cart:
        return {"message": "Keranjang belanja saat ini kosong.", "data": []}
    return {"message": "Isi keranjang berhasil diambil", "data": cart}


@router.delete("/cart/remove/{item_id}", status_code=status.HTTP_200_OK, tags=["User - Transaction"])
def remove_ticket_from_cart(item_id: str):
    global cart
    for idx, item in enumerate(cart):
        if item.get("item_id") == item_id:
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

    total_price = sum(item.get("price", 0) for item in cart)
    booked_tickets = []

    # Validasi ulang semua kursi sebelum finalisasi
    for item in cart:
        # 2. Perbaikan: Cari di 'list_jadwal' bukan 'schedule'
        schedule = next((s for s in list_jadwal if s.get("id") == item.get("schedule_id")), None)
        if not schedule or not schedule.get("seats", {}).get(item.get("seat_number"), {}).get("available"):
            raise HTTPException(
                status_code=400,
                detail=f"Checkout gagal. Kursi '{item.get('seat_number')}' untuk film '{item.get('movie_title')}' sudah tidak tersedia lagi."
            )

    # Proses checkout setelah semua valid
    for item in cart:
        # 3. Perbaikan: Cari lagi di 'list_jadwal'
        schedule = next((s for s in list_jadwal if s.get("id") == item.get("schedule_id")), None)
        if schedule:
            schedule["seats"][item["seat_number"]]["available"] = False
        
        booked_tickets.append(item)

    # Hasilkan kode booking
    booking_code = f"BK-{uuid.uuid4().hex[:8].upper()}"

    # Buat data transaksi
    new_transaction = {
        "booking_code": booking_code,
        "total_price": total_price,
        "tickets": booked_tickets
    }

    # Simpan ke riwayat dan kosongkan keranjang
    transaction_history.append(new_transaction)
    cart.clear()

    return {"message": "Checkout berhasil", "data": new_transaction}