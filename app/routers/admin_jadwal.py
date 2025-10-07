from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import HTMLResponse
from typing import List
from app.routers.admin_film import list_film  # ambil daftar film dari router film
from app.models import Schedule
from app.models import Movie
from pydantic import BaseModel

router = APIRouter(prefix="/admin/schedules", tags=["Admin - Jadwal"])

# Database sementara
studios = []
schedules = Schedule = []
schedule_counter = 1


# === FUNGSI: inisialisasi kursi ===
def init_seats():
    rows = 8
    cols_per_side = 6
    aisle_gap = 1
    seat_layout = []

    for r in range(rows):
        row_letter = chr(97 + r)  # a, b, c...
        row_seats = []

        # sisi kiri
        for c in range(1, cols_per_side + 1):
            row_seats.append({"seat": f"{row_letter}{c}", "available": True})

        # lorong tengah
        for _ in range(aisle_gap):
            row_seats.append({"seat": " ", "available": None})

        # sisi kanan
        for c in range(cols_per_side + 1, cols_per_side * 2 + 1):
            row_seats.append({"seat": f"{row_letter}{c}", "available": True})

        seat_layout.append(row_seats)
    return seat_layout


# === CREATE beberapa jadwal sekaligus ===
@router.post("/")
@router.post("/schedules")
def buat_jadwal(schedule: Schedule):
    global schedule_counter
    # cari film dari list_film yang diimport dari admin_film
    for f in list_film:
        if f["id"] == schedule.movie_id:
            movie = f
            break
        else:
            raise HTTPException(status_code=404, detail="Film tidak ditemukan")
    new_schedule = {
        "id": schedule_counter,
        "movie_id": movie["id"],
        "movie_title": movie["title"],
        "duration": movie["duration"],
        "studio": studio,
        "date": date,
        "time": time,
        "seats": init_seats()}
    schedules.append(new_schedule)
    schedule_counter += 1
    return {"message": "Beberapa jadwal berhasil dibuat", "schedules": new_schedule}


# === READ jadwal per film ===
@router.get("/movies/{movie_id}")
def get_schedules_for_movie(movie_id: str):
    movie_schedules = [s for s in schedules if s["movie_id"] == movie_id]
    if not movie_schedules:
        raise HTTPException(status_code=404, detail="Tidak ada jadwal untuk film ini")
    return movie_schedules


# === UPDATE jadwal ===
@router.put("/{schedule_id}")
def update_schedule(schedule_id: int, date: str = None, time: str = None):
    for s in schedules:
        if s["id"] == schedule_id:
            if date:
                s["date"] = date
            if time:
                s["time"] = time
            return {"message": "Jadwal berhasil diperbarui", "schedule": s}
    raise HTTPException(status_code=404, detail="Jadwal tidak ditemukan")


# === DELETE jadwal ===
@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int):
    for s in schedules:
        if s["id"] == schedule_id:
            schedules.remove(s)
            return {"message": "Jadwal berhasil dihapus"}
    raise HTTPException(status_code=404, detail="Jadwal tidak ditemukan")


# === Tampilkan layout kursi (HTML) ===
@router.get("/{schedule_id}/seat-map", response_class=HTMLResponse)
def seat_map(schedule_id: int):
    schedule = next((s for s in schedules if s["id"] == schedule_id), None)
    if not schedule:
        raise HTTPException(status_code=404, detail="Jadwal tidak ditemukan")

    html = "<h3>Peta Kursi (Layar di bawah)</h3><table border='1' cellpadding='6' style='text-align:center;'>"
    for row in schedule["seats"]:
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

@router.post("/{schedule_id}/book")
def book_seats(schedule_id: int, seat_list: list[str] = Body(..., embed=True)):
    """
    User memesan kursi:
    - Maksimal 10 kursi
    - Tidak bisa pesan kursi yang sudah terisi
    """
    # Validasi input
    if len(seat_list) == 0:
        raise HTTPException(status_code=400, detail="Minimal pilih 1 kursi")
    if len(seat_list) > 10:
        raise HTTPException(status_code=400, detail="Maksimal 10 kursi per transaksi")

    # Cari jadwalnya
    schedule = next((s for s in schedules if s["id"] == schedule_id), None)
    if not schedule:
        raise HTTPException(status_code=404, detail="Jadwal tidak ditemukan")

    # Proses pemesanan
    booked = []
    for seat_code in seat_list:
        # cari kursi di semua baris
        seat = next((x for row in schedule["seats"] for x in row if x["seat"] == seat_code), None)
        if not seat:
            raise HTTPException(status_code=400, detail=f"Kursi {seat_code} tidak tersedia")
        if not seat["available"]:
            raise HTTPException(status_code=400, detail=f"Kursi {seat_code} sudah dipesan")

        seat["available"] = False
        booked.append(seat_code)

    return {
        "message": "Kursi berhasil dipesan!",
        "booked_seats": booked
    }
# End of file