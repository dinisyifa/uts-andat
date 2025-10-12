# app/routers/user_catalog.py
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

# Import data dari admin
from app.routers.admin_film import list_film
from app.routers.admin_jadwal import list_jadwal

router = APIRouter()

# ===============================
# GET /user/now_playing
# ===============================
@router.get("/now_playing")
def get_now_playing():
    """
    Menampilkan daftar semua film yang sedang tayang.
    (Mengambil dari list_film di admin_film.py)
    """
    if not list_film:
        raise HTTPException(status_code=404, detail="Tidak ada film yang sedang tayang.")

    data_ringkas = [
        {
            "id": film["id"],
            "title": film["title"],
            "genre": film.get("genre", "-"),
            "duration": film.get("duration", "-"),
            "rating_usia": film.get("rating_usia", "-"),
            "price": film.get("price", 0)
        }
        for film in list_film
    ]
    return {
        "message": "Daftar film yang sedang tayang berhasil diambil",
        "count": len(data_ringkas),
        "data": data_ringkas
    }


# ===============================
# GET /user/movies/{movie_id}/details
# ===============================
@router.get("/movies/{movie_id}/details")
def get_movie_details(movie_id: str):
    """
    Menampilkan detail film dan semua jadwal tayangnya.
    """
    # cari film
    movie = next((f for f in list_film if f["id"] == movie_id or f["id"] == f"mov{movie_id}"), None)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Film dengan ID {movie_id} tidak ditemukan.")

    # cari jadwal berdasarkan movie_id (cocokkan dengan atau tanpa prefix 'mov')
    movie_schedules = [
    j for j in list_jadwal
    if j["movie_id"].replace("mov", "") == movie["id"].replace("mov", "")
    ]

    return {
        "id": movie["id"],
        "title": movie["title"],
        "sutradara": movie.get("sutradara", "-"),
        "rating_usia": movie.get("rating_usia", "-"),
        "price": movie.get("price", "-"),
        "schedules": [
            {
                "id_jadwal": j["id_jadwal"],
                "studio": j["studio_name"],
                "tanggal": j["date"],
                "waktu": j["time"]
            } for j in movie_schedules
        ]
    }


# ===============================
# GET /user/schedules/{schedule_id}/seats
# ===============================
@router.get("/schedules/{schedule_id}/seats")
def get_seat_layout(schedule_id: str):
    """
    Menampilkan denah dan status ketersediaan kursi untuk jadwal tertentu.
    """
    jadwal = next((j for j in list_jadwal if j["id_jadwal"] == schedule_id), None)
    if not jadwal:
        raise HTTPException(status_code=404, detail=f"Jadwal dengan ID {schedule_id} tidak ditemukan.")

    seats = jadwal.get("seats", [])
    if not seats:
        raise HTTPException(status_code=404, detail="Data kursi tidak tersedia untuk jadwal ini.")

    # Buat list kursi yang bisa dipilih user
    seat_list = []
    for row in seats:
        for seat in row:
            if seat["available"] is not None:
                seat_list.append({
                    "seat_number": seat["seat"],
                    "status": "available" if seat["available"] else "booked"
                })

    return {
        "message": "Denah kursi berhasil diambil",
        "schedule_id": jadwal["id_jadwal"],
        "studio": jadwal["studio_name"],
        "available_seats": [s for s in seat_list if s["status"] == "available"],
        "all_seats": seat_list
    }
