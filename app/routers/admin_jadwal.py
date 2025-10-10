from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
from app.models import Schedule, Seat
from app.routers.admin_film import list_film, list_studio

router = APIRouter(prefix="/admin/jadwal", tags=["Admin - Jadwal"])

# helper untuk kursi
def init_seats() -> List[List[Seat]]:
    rows = 8
    cols_per_side = 6
    aisle_gap = 1
    seat_layout = []
    for r in range(rows):
        row_letter = chr(65 + r)  # A,B,C...
        row_seats = []
        for c in range(1, cols_per_side + 1):
            row_seats.append({"seat": f"{row_letter}{c}", "available": True})
        for _ in range(aisle_gap):
            row_seats.append({"seat": " ", "available": None})
        for c in range(cols_per_side + 1, cols_per_side * 2 + 1):
            row_seats.append({"seat": f"{row_letter}{c}", "available": True})
        seat_layout.append(row_seats)
    return seat_layout

# -------------------------
# preload database (list of dicts)
# -------------------------
# NOTE: list_jadwal stores dicts so existing user_catalog (which uses j.get(...)) tetap jalan

list_jadwal: List[Dict[str, Any]] = [
    Schedule(id_jadwal="sch1", movie_id="mov1", movie_title="Avengers: Endgame", studio_id="1", studio_name="Studio 1", date="2024-06-01", time="12.15 - 15.05", seats=None).dict(),
    Schedule(id_jadwal="sch2", movie_id="mov1", movie_title="Avengers: Endgame", studio_id="2", studio_name="Studio 2", date="2024-06-01", time="14.45 - 17.10", seats=None).dict(),
    Schedule(id_jadwal="sch3", movie_id="mov1", movie_title="Avengers: Endgame", studio_id="3", studio_name="Studio 3", date="2024-06-01", time="14.50 - 17.15", seats=None).dict(),
    Schedule(id_jadwal="sch4", movie_id="mov1", movie_title="Avengers: Endgame", studio_id="4", studio_name="Studio 4", date="2024-06-01", time="13.20 - 16.40", seats=None).dict(),
    Schedule(id_jadwal="sch5", movie_id="mov1", movie_title="Avengers: Endgame", studio_id="5", studio_name="Studio 5", date="2024-06-01", time="19.40 - 23.00", seats=None).dict(),
    Schedule(id_jadwal="sch6", movie_id="mov2", movie_title="The Conjuring", studio_id="2", studio_name="Studio 2", date="2024-06-01", time="12.15 - 14.15", seats=None).dict(),
    Schedule(id_jadwal="sch7", movie_id="mov2", movie_title="The Conjuring", studio_id="3", studio_name="Studio 3", date="2024-06-01", time="17.30 - 19.30", seats=None).dict(),
    Schedule(id_jadwal="sch8", movie_id="mov2", movie_title="The Conjuring", studio_id="4", studio_name="Studio 4", date="2024-06-01", time="17.00 - 19.00", seats=None).dict(),
    Schedule(id_jadwal="sch9", movie_id="mov2", movie_title="The Conjuring", studio_id="5", studio_name="Studio 5", date="2024-06-01", time="10.00 - 12.10", seats=None).dict(),
    Schedule(id_jadwal="sch10", movie_id="mov2", movie_title="The Conjuring", studio_id="1", studio_name="Studio 1", date="2024-06-01", time="12.10 - 14.10", seats=None).dict(),
    Schedule(id_jadwal="sch11", movie_id="mov3", movie_title="Frozen", studio_id="3", studio_name="Studio 3", date="2024-06-01", time="10.00 - 12.10", seats=None).dict(),
    Schedule(id_jadwal="sch12", movie_id="mov3", movie_title="Frozen", studio_id="4", studio_name="Studio 4", date="2024-06-01", time="19.20 - 20.30", seats=None).dict(),
    Schedule(id_jadwal="sch13", movie_id="mov3", movie_title="Frozen", studio_id="5", studio_name="Studio 5", date="2024-06-01", time="16.55 - 19.15", seats=None).dict(),
    Schedule(id_jadwal="sch14", movie_id="mov3", movie_title="Frozen", studio_id="1", studio_name="Studio 1", date="2024-06-01", time="17.00 - 19.10", seats=None).dict(),
    Schedule(id_jadwal="sch15", movie_id="mov3", movie_title="Frozen", studio_id="2", studio_name="Studio 2", date="2024-06-01", time="17.40 - 20.00", seats=None).dict(),
    Schedule(id_jadwal="sch16", movie_id="mov4", movie_title="Komang", studio_id="4", studio_name="Studio 4", date="2024-06-01", time="11.00 - 13.10", seats=None).dict(),
    Schedule(id_jadwal="sch17", movie_id="mov4", movie_title="Komang", studio_id="5", studio_name="Studio 5", date="2024-06-01", time="14.45 - 16.55", seats=None).dict(),
    Schedule(id_jadwal="sch18", movie_id="mov4", movie_title="Komang", studio_id="1", studio_name="Studio 1", date="2024-06-01", time="10.00 - 12.10", seats=None).dict(),
    Schedule(id_jadwal="sch19", movie_id="mov4", movie_title="Komang", studio_id="2", studio_name="Studio 2", date="2024-06-01", time="20.30 - 22.40", seats=None).dict(),
    Schedule(id_jadwal="sch20", movie_id="mov4", movie_title="Komang", studio_id="3", studio_name="Studio 3", date="2024-06-01", time="20.00 - 22.10", seats=None).dict(),
    Schedule(id_jadwal="sch21", movie_id="mov5", movie_title="Detective Conan: One-eyed Flashback", studio_id="1", studio_name="Studio 1", date="2024-06-01", time="14.30 - 16.35", seats=None).dict(),
    Schedule(id_jadwal="sch22", movie_id="mov5", movie_title="Detective Conan: One-eyed Flashback", studio_id="2", studio_name="Studio 2", date="2024-06-01", time="10.00 - 12.05", seats=None).dict(),
    Schedule(id_jadwal="sch23", movie_id="mov5", movie_title="Detective Conan: One-eyed Flashback", studio_id="3", studio_name="Studio 3", date="2024-06-01", time="12.15 - 14.10", seats=None).dict(),
    Schedule(id_jadwal="sch24", movie_id="mov5", movie_title="Detective Conan: One-eyed Flashback", studio_id="4", studio_name="Studio 4", date="2024-06-01", time="20.40 - 22.45", seats=None).dict(),
]

# pastikan seats dibuat (jika None)
for j in list_jadwal:
    if not j.get("seats"):
        j["seats"] = init_seats()

# counter (agar id baru tidak bentrok)
schedule_counter = len(list_jadwal) + 1

# =======================
# ENDPOINTS
# =======================
@router.get("/schedules")
def lihat_semua_jadwal():
    return {"message": "Daftar semua jadwal berhasil diambil", "data": list_jadwal}


@router.get("/movies/{movie_id}")
def lihat_jadwal_film(movie_id: str):
    jadwal_film = [j for j in list_jadwal if str(j.get("movie_id")) == str(movie_id)]
    if not jadwal_film:
        raise HTTPException(status_code=404, detail="Belum ada jadwal untuk film ini")
    return {"message": f"Jadwal untuk film {movie_id} berhasil diambil", "data": jadwal_film}


@router.post("/schedules")
def tambah_jadwal(schedule: Schedule):
    """Menambahkan jadwal baru"""
from app.models import Schedule, Seat
from app.routers.admin_film import list_film

@router.post("/schedules")
def tambah_jadwal(schedule: Schedule):
    # pastikan film valid
    film = next((f for f in list_film if f["id"] == schedule.movie_id), None)
    if not film:
        raise HTTPException(status_code=404, detail="Film tidak ditemukan")

    # buat jadwal baru
    new_schedule = schedule.dict()
    new_schedule["id_jadwal"] = f"sch{len(list_jadwal) + 1}"
    new_schedule["movie_title"] = film["title"]
    new_schedule["seats"] = init_seats()

    list_jadwal.append(new_schedule)
    return {"message": "Jadwal berhasil dibuat", "data": new_schedule}



@router.delete("/{schedule_id}")
def hapus_jadwal(schedule_id: str):
    for j in list_jadwal:
        if j.get("id_jadwal") == schedule_id:
            list_jadwal.remove(j)
            return {"message": f"Jadwal {schedule_id} berhasil dihapus"}
    raise HTTPException(status_code=404, detail="Jadwal tidak ditemukan")


@router.get("/{schedule_id}/seat-map", response_class=HTMLResponse)
def seat_map(schedule_id: str):
    jadwal = next((j for j in list_jadwal if j.get("id_jadwal") == schedule_id), None)
    if not jadwal:
        raise HTTPException(status_code=404, detail="Jadwal tidak ditemukan")
    html = "<h3>Peta Kursi (Layar di bawah)</h3><table border='1' cellpadding='6' style='text-align:center;'>"
    for row in jadwal["seats"]:
        html += "<tr>"
        for seat in row:
            if seat["available"] is None:
                html += "<td style='background:white; width:20px;'></td>"
            elif seat["available"]:
                html += f"<td style='background:lightgreen; width:30px'>{seat['seat']}</td>"
            else:
                html += f"<td style='background:lightgray; width:30px'>{seat['seat']}</td>"
        html += "</tr>"
    html += "</table><p style='margin-top:10px;'>===== LAYAR BIOSKOP =====</p>"
    return html