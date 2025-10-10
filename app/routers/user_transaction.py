# file: app/routers/user_transaction.py

import uuid
from typing import List
from fastapi import APIRouter, HTTPException, status
from app.models import CartAddItem, CartItemResponse, TransactionDetail, PaymentMethodRequest, PreTransactionResponse

from app.routers.admin_film import list_film
from app.routers.admin_jadwal import list_jadwal

# variabel global
cart = []
transaction_history = []
pending_orders = {}

router = APIRouter()

# ==========================================
# API - MANAJEMEN KERANJANGB (USER)
# ==========================================

@router.post("/cart/add")
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


@router.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Keranjang belanja saat ini kosong.", "data": []}
    return {"message": "Isi keranjang berhasil diambil", "data": cart}


@router.delete("/cart/remove/{item_id}")
def remove_ticket_from_cart(item_id: str):
    global cart
    for idx, item in enumerate(cart):
        if item.get("item_id") == item_id:
            del cart[idx]
            return {"message": f"Item dengan ID {item_id} berhasil dihapus dari keranjang"}
    raise HTTPException(status_code=404, detail=f"Item dengan ID '{item_id}' tidak ditemukan di keranjang.")


# ==========================================
# API - PROSES CHECKOUT DUA LANGKAH (BARU)
# ==========================================

# LANGKAH 1: User memilih metode pembayaran
@router.post("/checkout/payment", response_model=PreTransactionResponse)
def select_payment_method(payload: PaymentMethodRequest):
    if not cart:
        raise HTTPException(status_code=400, detail="Keranjang belanja kosong.")

    # Validasi ulang semua kursi sebelum membuat pesanan sementara
    for item in cart:
        schedule = next((s for s in list_jadwal if s.get("id") == item.get("schedule_id")), None)
        if not schedule or not schedule.get("seats", {}).get(item.get("seat_number"), {}).get("available"):
            raise HTTPException(
                status_code=409,
                detail=f"Checkout gagal. Kursi '{item.get('seat_number')}' sudah tidak tersedia lagi."
            )

    # Buat pesanan sementara
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    total_price = sum(item.get("price", 0) for item in cart)

    # Buat daftar tiket yang bersih untuk respons
    clean_tickets = []
    for item in cart:
        clean_ticket = {
            "item_id": item.get("item_id"), "movie_title": item.get("movie_title"),
            "schedule": item.get("schedule"), "studio": item.get("studio"),
            "seat_number": item.get("seat_number"), "price": item.get("price")
        }
        clean_tickets.append(clean_ticket)
    
    # Simpan data pesanan sementara di memori
    pending_orders[order_id] = {
        "total_price": total_price,
        "payment_method": payload.payment_method,
        "tickets_full_data": list(cart) # Simpan data lengkap dari keranjang
    }

    # Kosongkan keranjang karena sudah masuk ke tahap pesanan
    cart.clear()

    # Kembalikan detail pesanan sementara ke user
    return PreTransactionResponse(
        order_id=order_id,
        total_price=total_price,
        payment_method=payload.payment_method,
        tickets=clean_tickets
    )


# LANGKAH 2: User mengonfirmasi pesanan
@router.get("/checkout/{order_id}/confirm", response_model=TransactionDetail)
def confirm_checkout(order_id: str):
    # Cari pesanan sementara
    order = pending_orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pesanan tidak ditemukan atau sudah kedaluwarsa.")

    # Jika valid, finalisasi transaksi
    # 1. Ubah status kursi menjadi "booked" secara permanen
    for item in order["tickets_full_data"]:
        schedule = next((s for s in list_jadwal if s.get("id") == item.get("schedule_id")), None)
        if schedule:
            schedule["seats"][item["seat_number"]]["available"] = False
    
    # 2. Hasilkan kode booking final
    booking_code = f"BK-{uuid.uuid4().hex[:8].upper()}"

    # 3. Buat data transaksi final
    final_transaction = {
        "booking_code": booking_code,
        "total_price": order["total_price"],
        "tickets": [
             {
                "item_id": item.get("item_id"), "movie_title": item.get("movie_title"),
                "schedule": item.get("schedule"), "studio": item.get("studio"),
                "seat_number": item.get("seat_number"), "price": item.get("price")
            } for item in order["tickets_full_data"]
        ]
    }
    
    # 4. Simpan ke riwayat transaksi
    transaction_history.append(final_transaction)
    
    # 5. Hapus dari daftar pesanan sementara
    pending_orders.pop(order_id, None)
    
    return TransactionDetail(**final_transaction)