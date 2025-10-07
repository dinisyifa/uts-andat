from fastapi import FastAPI, HTTPException

app = FastAPI()

movies = [
   {"id": 1, "title": "Avengers: Endgame", "duration": "200 menit", "price": 40000},
    {"id": 2, "title": "The Conjuring", "duration": "120 menit", "price": 40000},
    {"id": 3, "title": "Frozen", "duration": "130 menit", "price": 40000},
    {"id": 4, "title": "Komang", "duration": "130 menit", "price": 40000},
    {"id": 5, "title": "Detective Conan", "duration": "125 menit", "price": 40000},
]

studios = [
    {"id": 1, "name": "Studio 1", "rows": 6, "cols": 8},
    {"id": 2, "name": "Studio 2", "rows": 6, "cols": 8},
    {"id": 3, "name": "Studio 3", "rows": 6, "cols": 8},
    {"id": 4, "name": "Studio 4", "rows": 6, "cols": 8},
    {"id": 5, "name": "Studio 5", "rows": 6, "cols": 8}
]

schedules = [
    # Avengers
    {"movie_id": 1, "studio": 1, "time": "12.15 - 15.05"},
    {"movie_id": 1, "studio": 2, "time": "14.45 - 17.10"},
    {"movie_id": 1, "studio": 3, "time": "14.50 - 17.15"},
    {"movie_id": 1, "studio": 4, "time": "13.20 - 16.40"},
    {"movie_id": 1, "studio": 5, "time": "19.40 - 23.00"},

    # The Conjuring
    {"movie_id": 2, "studio": 2, "time": "12.15 - 14.15"},
    {"movie_id": 2, "studio": 3, "time": "17.30 - 19.30"},
    {"movie_id": 2, "studio": 4, "time": "17.00 - 19.00"},
    {"movie_id": 2, "studio": 5, "time": "10.00 - 12.10"},
    {"movie_id": 2, "studio": 1, "time": "12.10 - 14.10"},

    # Frozen
    {"movie_id": 3, "studio": 3, "time": "10.00 - 12.10"},
    {"movie_id": 3, "studio": 4, "time": "19.20 - 20.30"},
    {"movie_id": 3, "studio": 5, "time": "16.55 - 19.15"},
    {"movie_id": 3, "studio": 1, "time": "17.00 - 19.10"},
    {"movie_id": 3, "studio": 2, "time": "17.40 - 20.00"},
    
    # Komang
    {"movie_id": 4, "studio": 4, "time": "11.00 - 13.10"},
    {"movie_id": 4, "studio": 5, "time": "14.45 - 16.55"},
    {"movie_id": 4, "studio": 1, "time": "10.00 - 12.10"},
    {"movie_id": 4, "studio": 2, "time": "20.30 - 22.40"},
    {"movie_id": 4, "studio": 3, "time": "20.00 - 22.10"},

    # Detective Conan
    {"movie_id": 5, "studio": 5, "time": "12.20 - 14.25"},
    {"movie_id": 5, "studio": 1, "time": "14.30 - 16.35"},
    {"movie_id": 5, "studio": 2, "time": "10.00 - 12.05"},
    {"movie_id": 5, "studio": 3, "time": "12.15 - 14.10"},
    {"movie_id": 5, "studio": 4, "time": "20.40 - 22.45"},

]
schedule_counter = 1


# Fungsi bantu untuk buat kursi otomatis
def init_seats():
    """
    Membuat layout kursi simetris: 8 baris (A–H), 16 kolom (8 kiri + lorong + 8 kanan)
    """
    rows = 8
    cols_per_side = 8  # kiri dan kanan
    aisle_gap = 1       # kolom kosong di tengah untuk lorong

    seat_layout = []  # akan berisi baris-baris kursi

    for r in range(rows):
        row_letter = chr(65 + r)  # A, B, C, ..., H
        row_seats = []

        # blok kiri
        for c in range(1, cols_per_side + 1):
            row_seats.append({"seat": f"{row_letter}{c}", "available": True})

        # tambahkan lorong (kolom kosong di tengah)
        for _ in range(aisle_gap):
            row_seats.append({"seat": " ", "available": None})  # kosong

        # blok kanan
        for c in range(cols_per_side + 1, cols_per_side * 2 + 1):
            row_seats.append({"seat": f"{row_letter}{c}", "available": True})

        seat_layout.append(row_seats)

    return seat_layout

@app.get("/movies/schedules")
def get_all_movie_schedules():
    movie_showtimes = []

    for movie in movies:
        # Ambil semua jadwal film ini
        movie_schedules = [
            {"studio": s["studio"], "time": s["time"]}
            for s in schedules if s["movie_id"] == movie["id"]
        ]
        movie_showtimes.append({
            "title": movie["title"],
            "duration": movie["duration"],
            "price": movie["price"],
            "showtimes": movie_schedules
        })
    
    return movie_showtimes

@app.get("/schedules/{schedule_id}/seat-map", response_class=HTMLResponse)
def seat_map(schedule_id: int):
    schedule = next((s for s in schedules if s["id"] == schedule_id), None)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    html = "<h3>Peta Kursi (Layar di bawah)</h3><table border='1' cellpadding='6' style='text-align:center;'>"
    for row in schedule["seats"]:
        html += "<tr>"
        for seat in row:
            if seat["available"] is None:
                html += "<td style='background:white; width:20px;'></td>"  # lorong kosong
            elif seat["available"]:
                html += f"<td style='background:lightgreen; width:30px'>{seat['seat']}</td>"
            else:
                html += f"<td style='background:lightgray; width:30px'>{seat['seat']}</td>"
        html += "</tr>"
    html += "</table><p style='margin-top:10px;'>===== LAYAR BIOSKOP =====</p>"
    return html
    


@app.post("/schedules/multiple")
def create_multiple_schedules(
    movie_ids: List[int],
    studio_ids: List[int],
    date: str,
    time: str
):
    global schedule_counter
    created_schedules = []

    for movie_id in movie_ids:
        movie = next((m for m in movies if m["id"] == movie_id), None)
        if not movie:
            continue
        for studio_id in studio_ids:
            studio = next((s for s in studios if s["id"] == studio_id), None)
            if not studio:
                continue
            new_schedule = {
                "id": schedule_counter,
                "movie_id": movie_id,
                "movie_title": movie["title"],
                "studio_id": studio_id,
                "studio_name": studio["name"],
                "date": date,
                "time": time,
                "seats": init_seats()
            }
            schedules.append(new_schedule)
            created_schedules.append(new_schedule)
            schedule_counter += 1

    return {"message": "telah dibuat beberapa jadwal", "schedules": created_schedules}

@app.get("/movies/{movie_id}/schedules")
def get_schedules(movie_id: int):
    movie_schedules = [s for s in schedules if s["movie_id"] == movie_id]
    if not movie_schedules:
        raise HTTPException(status_code=404, detail="tidak ada jadwal untuk film ini")
    return movie_schedules


@app.put("/schedules/{schedule_id}")
def update_schedule(schedule_id: int, date: str = None, time: str = None):
    for s in schedules:
        if s["id"] == schedule_id:
            if date:
                s["date"] = date
            if time:
                s["time"] = time
            return {"message": "jadwal terbarui", "schedule": s}
    raise HTTPException(status_code=404, detail="jadwal tidak ditemukan")


@app.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: int):
    for s in schedules:
        if s["id"] == schedule_id:
            schedules.remove(s)
            return {"message": "jadwal berhasil dihapus"}
    raise HTTPException(status_code=404, detail="jadwal tidak tersedia")


#end point user
@app.get("/schedules/{schedule_id}/seats")
def view_seats(schedule_id: int):
    """Lihat semua kursi dan status ketersediaannya."""
    schedule = next((s for s in schedules if s["id"] == schedule_id), None)
    if not schedule:
        raise HTTPException(status_code=404, detail="jadwal tidak tersedia")
    return {"schedule_id": schedule_id, "seats": schedule["seats"]}


@app.post("/schedules/{schedule_id}/book")
def book_seats(schedule_id: int, seat_list: list[str] = Body(..., embed=True)):
    """
    User memesan kursi.
    - Maks 10 kursi per pemesanan
    - Tidak bisa memilih kursi yang sudah terisi
    """
    # Validasi jumlah kursi
    if len(seat_list) == 0:
        raise HTTPException(status_code=400, detail="anda harus memilih minimal 1 kursi")
    if len(seat_list) > 10:
        raise HTTPException(status_code=400, detail="anda hanya bisa memesan maksimal 10 kursi")

    # Cari jadwal
    schedule = next((s for s in schedules if s["id"] == schedule_id), None)
    if not schedule:
        raise HTTPException(status_code=404, detail="jadwal tidak tersedia")

    # Validasi ketersediaan kursi
    booked = []
    for seat_code in seat_list:
        seat = next((x for x in schedule["seats"] if x["seat"] == seat_code), None)
        if not seat:
            raise HTTPException(status_code=400, detail=f"kursi {seat_code} tidak tersedia")
        if not seat["available"]:
            raise HTTPException(status_code=400, detail=f"kursi {seat_code} sudah di pesan")
        # Tandai kursi jadi tidak tersedia
        seat["available"] = False
        booked.append(seat_code)

    return {
        "message": "kursi berhasil di pesan ",
        "booked_seats": booked,
        "remaining_available": sum(1 for s in schedule["seats"] if s["available"])
    }