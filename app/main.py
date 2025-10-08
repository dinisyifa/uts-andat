# main.py
# ==========================================
# Entry point utama aplikasi FastAPI
# ==========================================

from fastapi import FastAPI
from app.routers import admin_film , admin_jadwal, user_catalog, user_transaction 

# Inisialisasi aplikasi FastAPI
app = FastAPI(
    title="Movie Booking System",
    description="Sistem pemesanan tiket bioskop sederhana",
    version="1.1.0"
)


# Registrasi router (Admin Film & Studio)
app.include_router(admin_film.router, tags=["Admin - Film & Studio"])
app.include_router(admin_jadwal.router, tags=["Admin - Jadwal"])
app.include_router(user_catalog.router, tags=["User - Catalog"])
app.include_router(user_transaction.router, tags=["User - Transaction"])


# Endpoint root (opsional, hanya untuk cek server jalan)
@app.get("/")
def home():
    return {
        "message": "Selamat datang di Movie Booking System!",
        "info": "Gunakan endpoint /docs untuk mencoba semua fitur API."
    }
