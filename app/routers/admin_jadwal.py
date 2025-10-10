from fastapi import APIRouter, HTTPException
from app.routers.admin_film import list_film, list_studio  # ambil data dari admin_film
from app.models import Movie, Studio, Schedule

router = APIRouter()

# Simpan jadwal di memori
list_jadwal = [
    Schedule(
        id_jadwal="sch1",
        movie_id="mov1",
        movie_title="Avengers: Endgame",
        studio_id="st1",
        studio_name="Studio 1",
        date="2025-10-15",  # contoh tanggal, sesuaikan dengan kebutuhan
        time="12.15 - 15.05",
        seats=None
    ),
    Schedule(
        id_jadwal="sch2",
        movie_id="mov1",
        movie_title="Avengers: Endgame",
        studio_id="st2",
        studio_name="Studio 2",
        date="2025-10-15",
        time="14.45 - 17.10",
        seats=None
    ),
    Schedule(
        id_jadwal="sch3",
        movie_id="mov1",
        movie_title="Avengers: Endgame",
        studio_id="st3",
        studio_name="Studio 3",
        date="2025-10-15",
        time="14.50 - 17.15",
        seats=None
    ),
    Schedule(
        id_jadwal="sch4",
        movie_id="mov1",
        movie_title="Avengers: Endgame",
        studio_id="st4",
        studio_name="Studio 4",
        date="2025-10-15",
        time="13.20 - 16.40",
        seats=None
    ),
    Schedule(
        id_jadwal="sch5",
        movie_id="mov1",
        movie_title="Avengers: Endgame",
        studio_id="st5",
        studio_name="Studio 5",
        date="2025-10-15",
        time="19.40 - 23.00",
        seats=None
    ),
    Schedule(
        id_jadwal="sch6",
        movie_id="mov2",
        movie_title="The Conjuring",
        studio_id="st2",
        studio_name="Studio 2",
        date="2025-10-15",
        time="12.15 - 14.15",
        seats=None
    ),
    Schedule(
        id_jadwal="sch7",
        movie_id="mov2",
        movie_title="The Conjuring",
        studio_id="st3",
        studio_name="Studio 3",
        date="2025-10-15",
        time="17.30 - 19.30",
        seats=None
    ),
    Schedule(
        id_jadwal="sch8",
        movie_id="mov2",
        movie_title="The Conjuring",
        studio_id="st4",
        studio_name="Studio 4",
        date="2025-10-15",
        time="17.00 - 19.00",
        seats=None
    ),
    Schedule(
        id_jadwal="sch9",
        movie_id="mov2",
        movie_title="The Conjuring",
        studio_id="st5",
        studio_name="Studio 5",
        date="2025-10-15",
        time="10.00 - 12.10",
        seats=None
    ),
    Schedule(
        id_jadwal="sch10",
        movie_id="mov2",
        movie_title="The Conjuring",
        studio_id="st1",
        studio_name="Studio 1",
        date="2025-10-15",
        time="12.10 - 14.10",
        seats=None
    ),
    Schedule(
        id_jadwal="sch11",
        movie_id="mov3",
        movie_title="Frozen",
        studio_id="st3",
        studio_name="Studio 3",
        date="2025-10-15",
        time="10.00 - 12.10",
        seats=None
    ),
    Schedule(
        id_jadwal="sch12",
        movie_id="mov3",
        movie_title="Frozen",
        studio_id="st4",
        studio_name="Studio 4",
        date="2025-10-15",
        time="19.20 - 20.30",
        seats=None
    ),
    Schedule(
        id_jadwal="sch13",
        movie_id="mov3",
        movie_title="Frozen",
        studio_id="st5",
        studio_name="Studio 5",
        date="2025-10-15",
        time="16.55 - 19.15",
        seats=None
    ),
    Schedule(
        id_jadwal="sch14",
        movie_id="mov3",
        movie_title="Frozen",
        studio_id="st1",
        studio_name="Studio 1",
        date="2025-10-15",
        time="17.00 - 19.10",
        seats=None
    ),
    Schedule(
        id_jadwal="sch15",
        movie_id="mov3",
        movie_title="Frozen",
        studio_id="st2",
        studio_name="Studio 2",
        date="2025-10-15",
        time="17.40 - 20.00",
        seats=None
    ),
    Schedule(
        id_jadwal="sch16",
        movie_id="mov4",
        movie_title="Komang",
        studio_id="st4",
        studio_name="Studio 4",
        date="2025-10-15",
        time="11.00 - 13.10",
        seats=None
    ),
    Schedule(
        id_jadwal="sch17",
        movie_id="mov4",
        movie_title="Komang",
        studio_id="st5",
        studio_name="Studio 5",
        date="2025-10-15",
        time="14.45 - 16.55",
        seats=None
    ),
    Schedule(
        id_jadwal="sch18",
        movie_id="mov4",
        movie_title="Komang",
        studio_id="st1",
        studio_name="Studio 1",
        date="2025-10-15",
        time="10.00 - 12.10",
        seats=None
    ),
    Schedule(
        id_jadwal="sch19",
        movie_id="mov4",
        movie_title="Komang",
        studio_id="st2",
        studio_name="Studio 2",
        date="2025-10-15",
        time="20.30 - 22.40",
        seats=None
    ),
    Schedule(
        id_jadwal="sch20",
        movie_id="mov4",
        movie_title="Komang",
        studio_id="st3",
        studio_name="Studio 3",
        date="2025-10-15",
        time="20.00 - 22.10",
        seats=None
    ),
    Schedule(
        id_jadwal="sch21",
        movie_id="mov5",
        movie_title="Detective Conan: One-eyed Flashback",
        studio_id="st1",
        studio_name="Studio 1",
        date="2025-10-15",
        time="14.30 - 16.35",
        seats=None
    ),
    Schedule(
        id_jadwal="sch22",
        movie_id="mov5",
        movie_title="Detective Conan: One-eyed Flashback",
        studio_id="st2",
        studio_name="Studio 2",
        date="2025-10-15",
        time="10.00 - 12.05",
        seats=None
    ),
    Schedule(
        id_jadwal="sch23",
        movie_id="mov5",
        movie_title="Detective Conan: One-eyed Flashback",
        studio_id="st3",
        studio_name="Studio 3",
        date="2025-10-15",
        time="12.15 - 14.10",
        seats=None
    ),
    Schedule(
        id_jadwal="sch24",
        movie_id="mov5",
        movie_title="Detective Conan: One-eyed Flashback",
        studio_id="st4",
        studio_name="Studio 4",
        date="2025-10-15",
        time="20.40 - 22.45",
        seats=None
    )
]
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
def tambah_jadwal(movie_id: str, studio_id: str, date: str, time: str):
    global schedule_counter

    # Cek movie
    film = next((f for f in list_film if f["id"] == movie_id), None)
    if not film:
        raise HTTPException(status_code=404, detail="Film tidak ditemukan")

    # Cek studio
    studio = next((s for s in list_studio if s["id_studio"] == studio_id), None)
    if not studio:
        raise HTTPException(status_code=404, detail="Studio tidak ditemukan")

    # Buat jadwal baru
    jadwal_baru = {
        "id_jadwal": f"sch{schedule_counter}",
        "movie_id": movie_id,
        "movie_title": film["title"],
        "studio_id": studio_id,
        "studio_name": studio["id_studio"],
        "date": date,
        "time": time,
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
