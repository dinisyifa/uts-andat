# app/routers/user_catalog.py
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, List, Any

# ambil data Admin (Ressy & Dini)
from app.routers.admin_film import list_film      # list[dict]
from app.routers.admin_jadwal import list_jadwal  # list[dict]
from app.models import Movie, Studio, Schedule, CatalogDetail, SeatDetail

# ---------------------------
# Router & Konstanta Layout
# ---------------------------
router = APIRouter()

ROWS = 8
COLS = 12
AISLE_AFTER_COL = 6
ROW_LETTERS = [chr(ord("A") + i) for i in range(ROWS)]
LEGEND = {".": "available", "H": "held", "X": "sold"}

def _empty_matrix() -> List[List[str]]:
    return [["." for _ in range(COLS)] for _ in range(ROWS)]

# ---------------------------
# Seats State (in-memory)
# ---------------------------
def _sid(x: Any) -> str:
    """paksa id jadi string (aman kalau sumbernya int/str)."""
    return str(x)

SEATS_BY_SCHEDULE: Dict[str, List[List[str]]] = {}

def _ensure_matrix(schedule_id: Any) -> List[List[str]]:
    sid = _sid(schedule_id)
    if sid not in SEATS_BY_SCHEDULE:
        SEATS_BY_SCHEDULE[sid] = _empty_matrix()
    return SEATS_BY_SCHEDULE[sid]

# --- demo opsional (boleh dihapus kalau tak perlu) ---
TODAY = "2025-10-07"
for demo_id in ("101", "102", "103"):
    _ensure_matrix(demo_id)
# -----------------------------------------------------

# ---------------------------
# HOLD state (TTL 30 menit)
# ---------------------------
HOLD_TTL_MINUTES = 30
HOLDS: Dict[Tuple[str, str], datetime] = {}  # key = (schedule_id:str, "A1")

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

def _parse_label(label: str) -> Optional[Tuple[int, int]]:
    """'A1' -> (0,0), 'C10' -> (2,9)."""
    if not label:
        return None
    s = label.strip().upper()
    if len(s) < 2:
        return None
    row_char = s[0]
    if row_char not in ROW_LETTERS:
        return None
    num = s[1:]
    if not num.isdigit():
        return None
    col = int(num)
    if not (1 <= col <= COLS):
        return None
    r = ROW_LETTERS.index(row_char)
    c = col - 1
    return (r, c)

def _sweep_expired_holds():
    now = _utcnow()
    expired = []
    for (sched_id, seat_label), exp_at in list(HOLDS.items()):
        if exp_at <= now:
            idx = _parse_label(seat_label)
            if idx is not None and sched_id in SEATS_BY_SCHEDULE:
                r, c = idx
                if SEATS_BY_SCHEDULE[sched_id][r][c] == "H":
                    SEATS_BY_SCHEDULE[sched_id][r][c] = "."
            expired.append((sched_id, seat_label))
    for key in expired:
        HOLDS.pop(key, None)

def _set_hold(schedule_id: Any, labels: List[str]):
    ok, ng = [], []
    exp = _utcnow() + timedelta(minutes=HOLD_TTL_MINUTES)
    mat = _ensure_matrix(schedule_id)
    for label in labels:
        idx = _parse_label(label)
        if idx is None:
            ng.append((label, "invalid_label"))
            continue
        r, c = idx
        if mat[r][c] == ".":
            mat[r][c] = "H"
            HOLDS[(_sid(schedule_id), label.upper())] = exp
            ok.append(label.upper())
        else:
            ng.append((label.upper(), "not_available"))
    return ok, ng

def _confirm_sold(schedule_id: Any, labels: List[str]):
    ok, ng = [], []
    now = _utcnow()
    mat = _ensure_matrix(schedule_id)
    for label in labels:
        key = (_sid(schedule_id), label.upper())
        idx = _parse_label(label)
        if idx is None:
            ng.append((label, "invalid_label"))
            continue
        r, c = idx
        exp = HOLDS.get(key)
        if exp is None or exp <= now:
            ng.append((label.upper(), "hold_missing_or_expired"))
            continue
        if mat[r][c] == "H":
            mat[r][c] = "X"
            HOLDS.pop(key, None)
            ok.append(label.upper())
        else:
            ng.append((label.upper(), "not_on_hold"))
    return ok, ng

# ---------------------------
# Endpoints (User – Kursi)
# ---------------------------
@router.get("/studio/1/schedules/today")
def studio1_today():
    """Hanya demo: 3 jadwal statis untuk uji cepat."""
    studio1_schedules = [
        {"id": "101", "studio": "1", "film": "Film A", "tanggal": TODAY, "jam": "10:00-12:00"},
        {"id": "102", "studio": "1", "film": "Film B", "tanggal": TODAY, "jam": "13:00-15:00"},
        {"id": "103", "studio": "1", "film": "Film C", "tanggal": TODAY, "jam": "19:00-21:00"},
    ]
    return {"date": TODAY, "studio": "1", "schedules": studio1_schedules}

@router.get("/schedules/{schedule_id}/seats")
def seat_map(schedule_id: str):
    _ensure_matrix(schedule_id)
    _sweep_expired_holds()
    mat = SEATS_BY_SCHEDULE.get(_sid(schedule_id))
    if mat is None:
        raise HTTPException(status_code=404, detail="Jadwal tidak ditemukan")

    left  = " ".join(str(i) for i in range(1, AISLE_AFTER_COL + 1))
    right = " ".join(str(i) for i in range(AISLE_AFTER_COL + 1, COLS + 1))
    lines = ["          SCREEN", f"   {left}   {right}"]
    for r in range(ROWS):
        L = " ".join(mat[r][:AISLE_AFTER_COL])
        R = " ".join(mat[r][AISLE_AFTER_COL:])
        lines.append(f"{ROW_LETTERS[r]}  {L}   {R}")

    return {
        "schedule_id": _sid(schedule_id),
        "rows": ROWS,
        "cols": COLS,
        "aisle_after_col": AISLE_AFTER_COL,
        "legend": LEGEND,
        "labels": {"row_letters": ROW_LETTERS, "col_numbers": list(range(1, COLS + 1))},
        "seats": mat,
        "display": lines,
    }

@router.post("/schedules/{schedule_id}/hold")
def hold_seats(schedule_id: str, seats: str = Query(..., description="contoh: A1,B2,C10")):
    _ensure_matrix(schedule_id)
    _sweep_expired_holds()
    labels = [s.strip().upper() for s in seats.split(",") if s.strip()]
    if not labels:
        raise HTTPException(status_code=400, detail="No seats specified")
    ok, ng = _set_hold(schedule_id, labels)
    return {
        "schedule_id": _sid(schedule_id),
        "held": ok,
        "failed": [{"seat": s, "reason": reason} for s, reason in ng],
        "expires_at_utc": (_utcnow() + timedelta(minutes=HOLD_TTL_MINUTES)).isoformat()
    }

@router.post("/schedules/{schedule_id}/confirm")
def confirm_sold(schedule_id: str, seats: str = Query(..., description="kursi yang di-hold, contoh: A1,B2")):
    _ensure_matrix(schedule_id)
    _sweep_expired_holds()
    labels = [s.strip().upper() for s in seats.split(",") if s.strip()]
    if not labels:
        raise HTTPException(status_code=400, detail="No seats specified")
    ok, ng = _confirm_sold(schedule_id, labels)
    return {"schedule_id": _sid(schedule_id), "sold": ok, "failed": [{"seat": s, "reason": reason} for s, reason in ng]}

@router.post("/schedules/{schedule_id}/release")
def release_hold(schedule_id: str, seats: str = Query(..., description="lepas hold manual: A1,B2")):
    _ensure_matrix(schedule_id)
    _sweep_expired_holds()
    labels = [s.strip().upper() for s in seats.split(",") if s.strip()]
    mat = SEATS_BY_SCHEDULE.get(_sid(schedule_id))
    if mat is None:
        raise HTTPException(status_code=404, detail="Jadwal tidak ditemukan")
    released, not_released = [], []
    for label in labels:
        idx = _parse_label(label)
        if idx is None:
            not_released.append({"seat": label, "reason": "invalid_label"})
            continue
        r, c = idx
        if mat[r][c] == "H":
            mat[r][c] = "."
            HOLDS.pop((_sid(schedule_id), label.upper()), None)
            released.append(label.upper())
        else:
            not_released.append({"seat": label.upper(), "reason": "not_on_hold"})
    return {"schedule_id": _sid(schedule_id), "released": released, "failed": not_released}

# ---------------------------
# Endpoints (User – Film & Jadwal)
# ---------------------------
@router.get("/now_playing")
def now_playing():
    """Daftar film singkat (anggap semua film aktif = now playing)."""
    if not list_film:
        raise HTTPException(status_code=404, detail="Belum ada film")
    return {
        "count": len(list_film),
        "movies": [
            {"id": f.get("id"), "title": f.get("title"), "duration": f.get("duration"), "price": f.get("price")}
            for f in list_film
        ],
    }

@router.get("/movies")
def user_movies():
    """Katalog: film + semua showtimes dari Dini (auto-init kursi per jadwal)."""
    if not list_film:
        raise HTTPException(status_code=404, detail="Belum ada film")
    katalog = []
    for film in list_film:
        showtimes = []
        for j in list_jadwal:
            if str(j.get("movie_id")) == str(film.get("id")):
                sid = _sid(j.get("id_jadwal"))
                _ensure_matrix(sid)  # auto-init
                showtimes.append({
                    "schedule_id": sid,
                    "studio": j.get("studio_name"),
                    "date": j.get("date"),
                    "time": j.get("time"),
                })
        katalog.append({
            "id": film.get("id"),
            "title": film.get("title"),
            "duration": film.get("duration"),
            "price": film.get("price"),
            "showtimes": showtimes,
        })
    return {"movies": katalog}

@router.get("/movies/{movie_id}/details")
def movie_details(movie_id: str):
    """Detail film + jadwal + ringkasan kursi per jadwal (available/held/sold)."""
    film = next((f for f in list_film if str(f.get("id")) == str(movie_id)), None)
    if not film:
        raise HTTPException(status_code=404, detail="Film tidak ditemukan")

    showtimes = []
    for j in list_jadwal:
        if str(j.get("movie_id")) == str(movie_id):
            sid = _sid(j.get("id_jadwal"))
            _ensure_matrix(sid)  # auto-init
            showtimes.append({
                "schedule_id": sid,
                "studio": j.get("studio_name"),
                "date": j.get("date"),
                "time": j.get("time"),
            })

    summaries = []
    for s in showtimes:
        sid = s["schedule_id"]
        mat = _ensure_matrix(sid)
        flat = [cell for row in mat for cell in row]
        summaries.append({
            "schedule_id": sid,
            "available": flat.count("."),
            "held": flat.count("H"),
            "sold": flat.count("X"),
        })

    return {
        "movie": {
            "id": film.get("id"),
            "title": film.get("title"),
            "duration": film.get("duration"),
            "price": film.get("price"),
            "synopsis": film.get("synopsis"),
        },
        "showtimes": showtimes,
        "seat_summary": summaries,
    }
