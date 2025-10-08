# app/models.py
# ==========================================
# Semua model data yang digunakan di sistem
# ==========================================

from pydantic import BaseModel
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
    id_jadwal: Optional[str] = None  # akan diisi otomatis (sch1, sch2, dst)
    movie_id: str                   # relasi ke Movie
    movie_title: Optional[str] = None
    studio_id: str                  # relasi ke Studio
    studio_name: Optional[str] = None
    date: str
    time: str
    seats: Optional[List[List[Dict[str, Optional[bool]]]]] = None