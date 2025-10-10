from fastapi import APIRouter, HTTPException
from app.routers.admin_film import list_film, list_studio  # ambil data dari admin_film
from app.models import Movie, Studio, Schedule

router = APIRouter()

# Simpan jadwal di memori
list_jadwal = []
schedule_counter = 1  # untuk ID unik jadwal


# Fungsi bantu: inisialisasi layout kursi 8x16 (ada lorong tengah)
def init_seats():
    rows = 8
    cols_per_side = 8
    aisle_gap = 1
    seat_layout = []

    for r in range(rows):
        row_letter = chr(65 + r)  # A, B, C, ...
        row_seats = []

        for c in range(1, cols_per_side + 1):
            row_seats.append({"seat": f"{row_letter}{c}", "available": True})

        row_seats.append({"seat": " ", "available": None})  # lorong tengah

        for c in range(cols_per_side + 1, cols_per_side * 2 + 1):
            row_seats.append({"seat": f"{row_letter}{c}", "available": True})

        seat_layout.append(row_seats)

    return seat_layout


# CREATE - Tambah jadwal baru
@router.post("/schedules")
def tambah_jadwal(schedule: Schedule):
    global schedule_counter

    # Cek movie
    film = next((f for f in list_film if f["id"] == schedule.movie_id), None)
    if not film:
        raise HTTPException(status_code=404, detail="Film tidak ditemukan")

    # Cek studio
    studio = next((s for s in list_studio if s["id_studio"] == schedule.studio_id), None)
    if not studio:
        raise HTTPException(status_code=404, detail="Studio tidak ditemukan")

    # Buat jadwal baru
    jadwal_baru = {
        "id_jadwal": f"sch{schedule_counter}",
        "movie_id": schedule.movie_id,
        "movie_title": film["title"],
        "studio_id": schedule.studio_id,
        "studio_name": studio["id_studio"],
        "date": schedule.date,
        "time": schedule.time,
        "seats": init_seats()
    }

    list_jadwal.append(jadwal_baru)
    schedule_counter += 1

    return {"message": "Jadwal berhasil dibuat", "data": jadwal_baru}


# READ - Lihat semua jadwal
@router.get("/schedules")
def lihat_semua_jadwal():
    if not list_jadwal:
        raise HTTPException(status_code=404, detail="Belum ada jadwal yang terdaftar")
    return {"message": "Daftar semua jadwal berhasil diambil", "data": list_jadwal}


# READ - Lihat jadwal berdasarkan film
@router.get("/movies/{movie_id}/schedules")
def lihat_jadwal_film(movie_id: str):
    jadwal_film = [j for j in list_jadwal if j["movie_id"] == movie_id]
    if not jadwal_film:
        raise HTTPException(status_code=404, detail="Belum ada jadwal untuk film ini")
    return {"message": f"Jadwal untuk film {movie_id} ditemukan", "data": jadwal_film}