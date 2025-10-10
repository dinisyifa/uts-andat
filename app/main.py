# app/main.py
from fastapi import FastAPI
from app.routers import admin_film, admin_jadwal, user_catalog, user_transaction

app = FastAPI(
    title="Movie Booking System",
    description="Sistem pemesanan tiket bioskop sederhana",
    version="1.2.0",
)

# Admin
app.include_router(admin_film.router,  tags=["Admin - Film & Studio"])
app.include_router(admin_jadwal.router, tags=["Admin - Jadwal"])

# User
app.include_router(user_catalog.router,     tags=["User - Seats"])            # punyamu (seat/hold/confirm)
app.include_router(user_transaction.router, tags=["User - Cart & Checkout"])  # punyanya Lulu

@app.get("/")
def home():
    return {
        "message": "Movie Booking API aktif (Admin & User)",
        "info": "Cek /docs untuk Swagger UI.",
    }
