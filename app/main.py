from fastapi import FastAPI
from app.routers import (admin_film, admin_jadwal, user_catalog, user_transaction)

app = FastAPI(
    title="Movie Booking System API",
    description="API untuk sistem reservasi bioskop online tanpa database",
    version="1.0.0"
)

# Daftarkan semua router
app.include_router(admin_film.router, tags=["Admin_Film"])
app.include_router(admin_jadwal.router, tags=["Admin_Jadwal"])
app.include_router(user_catalog.router, tags=["User_Catalog"])
app.include_router(user_transaction.router, tags=["User_Transaction"])

@app.get("/")
def root():
    return {"message": "Selamat datang di Movie Booking System API!"}