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