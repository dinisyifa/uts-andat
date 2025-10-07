from fastapi import FastAPI
from app.routers import admin_film

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
