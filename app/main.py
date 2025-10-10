# app/main.py
from fastapi import FastAPI
from app.routers import admin_film, admin_jadwal, user_catalog, user_transaction

tags_metadata = [
    {
        "name": "Admin - Film & Studio",
        "description": "Operasi yang berhubungan dengan manajemen data film dan studio oleh Admin.",
    },
    {
        "name": "Admin - Jadwal",
        "description": "Operasi untuk mengelola jadwal tayang film oleh Admin.",
    },
    {
        "name": "User - Seats",
        "description": "Endpoint bagi pengguna untuk melihat katalog film, jadwal, dan denah kursi.",
    },
    {
        "name": "User - Cart & Checkout",
        "description": "Endpoint untuk mengelola keranjang belanja dan proses checkout oleh pengguna.",
    },
]

app = FastAPI(
    title="Movie Booking System",
    description="Sistem pemesanan tiket bioskop sederhana",
    version="1.2.0",
    openapi_tags=tags_metadata 
)

# ---------------------------

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
