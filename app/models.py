# app/models.py
# ==========================================
# Semua model data yang digunakan di sistem
# ==========================================

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


# ===============================
# MODEL UNTUK ADMIN FILM
# ===============================
class Movie(BaseModel):
    """
    Representasi data satu film yang dikelola oleh Admin.
    """
    id: str                 # contoh: "MOV001"
    title: str              # contoh: "Avengers: Endgame"
    duration: str           # contoh: "3h 20m"
    genre: str 
    sutradara: str
    rating_usia: str  # opsional (bisa diisi nanti)
    price: str              # contoh: 50000

# ===============================
# MODEL UNTUK STUDIO
# ===============================
class Studio(BaseModel):
    """
    Representasi data studio yang menayangkan film tertentu.
    Terhubung dengan data Movie melalui id_movie.
    """
    id_studio: str          # contoh: "st1"
    id_movie: str           # contoh: "mov1"
    title: str

# ===============================
# MODEL UNTUK JADWAL PENAYANGAN
# ===============================
class Schedule(BaseModel):
    """
    Representasi satu jadwal penayangan film di studio tertentu.
    """
    id_jadwal: Optional[str] = None     # akan diisi otomatis (sch1, sch2, dst)
    movie_id: str                       # relasi ke Movie
    movie_title: Optional[str] = None
    studio_id: str                      # relasi ke Studio
    studio_name: Optional[str] = None
    date: str
    time: str
    seats: Optional[List[List[Dict[str, Optional[bool]]]]] = None


# ===============================
# MODEL UNTUK KERANJANG BELANJA
# ===============================

# Model untuk request body saat menambahkan item ke keranjang
class CartAddItem(BaseModel):
    """
    Representasi data input dari user saat menambahkan tiket ke keranjang.
    Hanya berisi informasi esensial yang dipilih oleh user.
    """
    schedule_id: str = Field(..., description="ID unik dari jadwal yang dipilih", example="SCH001")
    seat_number: str = Field(..., description="Nomor kursi yang dipilih oleh user", example="A5")

# Model untuk merepresentasikan satu item di dalam keranjang
class CartItemResponse(BaseModel):
    """
    Representasi data satu tiket yang ada di dalam keranjang belanja.
    Informasi ini dirakit oleh sistem berdasarkan input dari CartAddItem.
    """
    item_id: str          # contoh: "ITEM-A1B2C3"
    movie_title: str      # contoh: "Avengers: Endgame"
    schedule: str         # contoh: "2025-10-08 19:00"
    studio: str           # contoh: "Studio 1"
    seat_number: str      # contoh: "A5"
    price: int            # contoh: 50000

# Model untuk respons detail transaksi setelah checkout berhasil
class TransactionDetail(BaseModel):
    """
    Representasi data dari sebuah transaksi yang sudah selesai.
    Dihasilkan setelah user melakukan checkout keranjang belanjanya.
    """
    booking_code: str                   # contoh: "BK-D4E5F6A7"
    total_price: int                    # contoh: 100000
    tickets: List[CartItemResponse]     # Daftar lengkap tiket yang dibeli