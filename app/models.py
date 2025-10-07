# app/models.py
# ==========================================
# Semua model data yang digunakan di sistem
# ==========================================

from pydantic import BaseModel
from typing import Optional, List, Dict


# ===============================
# 1️⃣ MODEL UNTUK ADMIN FILM
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
    rating: Optional[float] = None  # opsional (bisa diisi nanti)
    price: int              # contoh: 50000


# ===============================
# 2️⃣ MODEL UNTUK ADMIN JADWAL    
# ===============================
class Schedule(BaseModel):
    """
    Representasi data satu jadwal tayang film di studio tertentu.
    """
    id: int                 # contoh: 1
    movie_id: int           # contoh: 1 (ID film yang dijadwalkan)
    studio_id: int          # contoh: 1 (ID studio tempat film ditayangkan)
    date: str               # contoh: "2023-10-01"
    time: str               # contoh: "19:00"
    seats: List[Dict]       # contoh: [{"seat": "a1", "available": True}, ...]