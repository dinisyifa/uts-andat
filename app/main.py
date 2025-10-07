from fastapi import FastAPI
from app.routers import admin_film, admin_jadwal, user_catalog, user_transaction
from fastapi import APIRouter, HTTPException, Body
from app.routers.admin_jadwal import schedules

#tambahan untuk jadwal
router = APIRouter(prefix="/user/transaction", tags=["User - Transaction"])

# Inisialisasi aplikasi FastAPI
app = FastAPI(
    title="Movie Booking System",
    description="Sistem pemesanan tiket bioskop sederhana (versi Person 1 - Manajemen Film)",
    version="1.0.0"
)

# Tambahkan router untuk fitur Admin Film
app.include_router(admin_film.router, tags=["Admin - Film"])

# Endpoint root (opsional, hanya untuk cek server jalan)
@app.get("/")
def home():
    return {
        "message": "Selamat datang di Movie Booking System!",
        "info": "Gunakan endpoint /docs untuk melihat dokumentasi API."
    }


#router untuk fitur Admin Jadwal
app.include_router(admin_film.router)
app.include_router(admin_jadwal.router)
app.include_router(user_catalog.router)
app.include_router(user_transaction.router)