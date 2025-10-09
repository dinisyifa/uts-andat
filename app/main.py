# app/main.py
# ==========================================
# Entry point utama aplikasi FastAPI
# ==========================================

from fastapi import FastAPI
from app.routers import admin_film, admin_jadwal, user_catalog  # semua router

# Inisialisasi aplikasi FastAPI
app = FastAPI(
    title="Movie Booking System",
    description="Sistem pemesanan tiket bioskop sederhana",
    version="1.1.0",
)

# Registrasi router
app.include_router(admin_film.router, tags=["Admin - Film & Studio"])
app.include_router(admin_jadwal.router, tags=["Admin - Jadwal"])
app.include_router(user_catalog.router, tags=["User"])

# Endpoint root (cek server)
@app.get("/")
def home():
    return {
        "message": "Movie Booking API aktif (Admin & User)",
        "info": "Coba /docs untuk Swagger UI.",
    }
