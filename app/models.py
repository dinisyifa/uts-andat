# app/models.py
# ==========================================
# Semua model data yang digunakan di sistem
# ==========================================

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# ===============================
# MODEL UNTUK ADMIN FILM #ressy
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
# MODEL UNTUK STUDIO #ressy
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
# MODEL UNTUK JADWAL PENAYANGAN #dini
# ===============================
class Seat(BaseModel):
    seat: str
    available: bool

class Schedule(BaseModel):
    """
    Representasi satu jadwal penayangan film di studio tertentu.
    """
    id_jadwal: Optional[str] = None
    movie_id: str
    studio_id: str
    date: str
    time: str
    movie_title: Optional[str] = None
    studio_name: Optional[str] = None
    seats: Optional[List[List[Seat]]] = None



# ==================================
# MODEL UNTUK DETAIL FILM DI KATALOG (USER) #tiffany
# ==================================
class CatalogDetail(BaseModel):
    """
    Model untuk menampilkan detail film di katalog (user).
    """
    id: str
    title: str
    duration: str
    genre: str
    sutradara: str
    rating_usia: str
    price: str
    schedules: List[Schedule]  # daftar jadwal terkait film ini

# ==================================
# MODEL UNTUK DETAIL KURSI #tiffany
# ==================================
class SeatDetail(BaseModel):
    """
    Model untuk menampilkan detail kursi yang dipilih.
    """
    seat_number: str
    is_booked: bool
    user_id: Optional[str] = None

# ==================================
# MODEL UNTUK MANAJEMEN KERANJANG & TRANSAKSI (USER)
# ==================================
class CartAddItem(BaseModel):
    """
    Model untuk menambah item tiket ke keranjang.
    """
    schedule_id: str      # ID jadwal (relasi ke Schedule)
    seat_number: str      # nomor kursi yang dipilih (misal: "A1")
    # quantity: int         # jumlah tiket (default 1, karena tiap kursi unik)
    # price: Optional[int] = None  # akan diisi otomatis dari data film
    # total_price: Optional[int] = None  # akan dihitung otomatis
    # movie_id: Optional[str] = None  # akan diisi otomatis dari data jadwal

# ==================================
class CartItemResponse(BaseModel):
    """
    Model untuk menampilkan item tiket di keranjang.
    """
    item_id: str          # ID unik item di keranjang (misal: "ITEM001")
    schedule_id: str
    movie_id: str
    movie_title: str
    schedule: str         # gabungan date + time (misal: "2023-10-01 19:00")
    studio: str
    seat_number: str
    price: int

# ==================================
# MODEL UNTUK DETAIL TRANSAKSI #lulu
# ==================================
class TransactionDetail(BaseModel):
    """
    Model untuk detail transaksi tiket.
    """
    transaction_id: str
    user_id: str
    schedule_id: str
    seats: List[str]
    total_price: int


# ===============================================
# MODEL BARU UNTUK ALUR CHECKOUT DUA LANGKAH
# ===============================================

class PaymentMethodRequest(BaseModel):
    """
    Model input dari user untuk memilih metode pembayaran.
    """
    payment_method: str = Field(..., description="Metode pembayaran yang dipilih", example="QRIS")

class PreTransactionResponse(BaseModel):
    """
    Model respons setelah user memilih metode pembayaran.
    Berisi ID pesanan sementara yang akan digunakan untuk konfirmasi.
    """
    order_id: str
    total_price: int
    payment_method: str
    expires_at: datetime # Menunjukkan kapan pesanan sementara ini akan batal
    tickets: List[CartItemResponse]