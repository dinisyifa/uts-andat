# app/routers/user_catalog.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Tuple
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

# ---- helpers: seat label <-> index ----
from typing import Optional, Tuple, Dict

def _parse_label(label: str) -> Optional[Tuple[int, int]]:
    """
    'A1' -> (0,0), 'C10' -> (2,9). Return None jika format/range salah.
    """
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

# Ganti anotasi ini (biar aman untuk Python 3.8/3.9)
# HOLDS: dict[tuple[int, str], datetime] = {}
HOLDS: Dict[Tuple[int, str], datetime] = {}


# router utama untuk bagian user (ini wajib)
router = APIRouter(prefix="/user", tags=["User"])
# ukuran layout studio
ROWS = 8
COLS = 12
AISLE_AFTER_COL = 6
ROW_LETTERS = [chr(ord("A") + i) for i in range(ROWS)]
LEGEND = {".": "available", "H": "held", "X": "sold"}  # (kalau kamu pakai 'booked' juga ok)

def _empty_matrix():
    return [["." for _ in range(COLS)] for _ in range(ROWS)]


# =======================
# STATE & HOLD (30 menit)
# =======================
from datetime import datetime, timedelta, timezone

# 3 jadwal untuk Studio 1 (contoh hari ini)
TODAY = "2025-10-07"  # biar gampang demo; kalau mau dinamis, pakai date.today().isoformat()
studio1_schedules = [
    {"id": 101, "studio": "1", "film": "Film A", "tanggal": TODAY, "jam": "10:00-12:00"},
    {"id": 102, "studio": "1", "film": "Film B", "tanggal": TODAY, "jam": "13:00-15:00"},
    {"id": 103, "studio": "1", "film": "Film C", "tanggal": TODAY, "jam": "19:00-21:00"},
]

# Kursi per jadwal (12 kolom, 8 baris, dengan lorong tengah: 6 | 6)
def _empty_matrix():
    return [["." for _ in range(COLS)] for _ in range(ROWS)]

SEATS_BY_SCHEDULE = {
    101: _empty_matrix(),
    102: _empty_matrix(),
    103: _empty_matrix(),
}

# Map HOLD: key = (schedule_id, "A1"), value = expire_at (UTC)
HOLD_TTL_MINUTES = 30
HOLDS: dict[tuple[int, str], datetime] = {}

def _utcnow():
    return datetime.now(timezone.utc)

def _sweep_expired_holds():
    """
    Kembalikan kursi ke '.' bila hold sudah lewat expire_at.
    Dipanggil setiap request yang terkait seats agar state konsisten.
    """
    now = _utcnow()
    expired = []
    for (sched_id, seat_label), exp_at in HOLDS.items():
        if exp_at <= now:
            # lepas hold di matrix
            idx = _parse_label(seat_label)
            if idx is not None and sched_id in SEATS_BY_SCHEDULE:
                r, c = idx
                # hanya lepaskan kalau masih 'H'
                if SEATS_BY_SCHEDULE[sched_id][r][c] == "H":
                    SEATS_BY_SCHEDULE[sched_id][r][c] = "."
            expired.append((sched_id, seat_label))
    for key in expired:
        HOLDS.pop(key, None)

def _set_hold(schedule_id: int, labels: list[str]):
    """
    Set kursi -> 'H' bila available; set expire = now + 30m
    Return tuple(list_sukses, list_gagal) untuk feedback user.
    """
    ok, ng = [], []
    now = _utcnow()
    exp = now + timedelta(minutes=HOLD_TTL_MINUTES)
    mat = SEATS_BY_SCHEDULE.get(schedule_id)
    if mat is None:
        return [], [(lbl, "schedule_not_found") for lbl in labels]

    for label in labels:
        idx = _parse_label(label)
        if idx is None:
            ng.append((label, "invalid_label"))
            continue
        r, c = idx
        if mat[r][c] == ".":
            mat[r][c] = "H"
            HOLDS[(schedule_id, label.upper())] = exp
            ok.append(label.upper())
        else:
            # sudah H / X
            ng.append((label.upper(), "not_available"))
    return ok, ng

def _confirm_sold(schedule_id: int, labels: list[str]):
    """
    Ubah 'H' menjadi 'X' bila hold masih aktif.
    """
    ok, ng = [], []
    now = _utcnow()
    mat = SEATS_BY_SCHEDULE.get(schedule_id)
    if mat is None:
        return [], [(lbl, "schedule_not_found") for lbl in labels]

    for label in labels:
        key = (schedule_id, label.upper())
        idx = _parse_label(label)
        if idx is None:
            ng.append((label, "invalid_label"))
            continue
        r, c = idx
        exp = HOLDS.get(key)
        if exp is None or exp <= now:
            # tidak ada hold aktif
            ng.append((label.upper(), "hold_missing_or_expired"))
            continue
        if mat[r][c] == "H":
            mat[r][c] = "X"
            HOLDS.pop(key, None)  # hapus hold
            ok.append(label.upper())
        else:
            ng.append((label.upper(), "not_on_hold"))
    return ok, ng

@router.get("/studio/1/schedules/today")
def studio1_today():
    """Lihat 3 jadwal hari ini untuk Studio 1 (demo)."""
    return {"date": TODAY, "studio": "1", "schedules": studio1_schedules}

@router.get("/schedules/{schedule_id}/seats")
def seat_map(schedule_id: int):
    _sweep_expired_holds()  # kalau kamu sudah buat fungsi ini
    try:
        seats = SEATS_BY_SCHEDULE[schedule_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Jadwal tidak ditemukan")

    # header angka kolom kiri-kanan + ASCII display
    left  = " ".join(str(i) for i in range(1, AISLE_AFTER_COL + 1))
    right = " ".join(str(i) for i in range(AISLE_AFTER_COL + 1, COLS + 1))
    lines = ["          SCREEN", f"   {left}   {right}"]
    for r in range(ROWS):
        L = " ".join(seats[r][:AISLE_AFTER_COL])
        R = " ".join(seats[r][AISLE_AFTER_COL:])
        lines.append(f"{ROW_LETTERS[r]}  {L}   {R}")

    return {
        "schedule_id": schedule_id,
        "rows": ROWS,
        "cols": COLS,
        "aisle_after_col": AISLE_AFTER_COL,
        "legend": LEGEND,
        "labels": {"row_letters": ROW_LETTERS, "col_numbers": list(range(1, COLS + 1))},
        "seats": seats,
        "display": lines,
    }


@router.post("/schedules/{schedule_id}/hold")
def hold_seats(schedule_id: int, seats: str = Query(..., description="contoh: A1,B2,C10")):
    """
    Hold kursi selama 30 menit (default). Kalau setelah 30 menit tidak di-confirm, otomatis lepas.
    """
    _sweep_expired_holds()
    labels = [s.strip().upper() for s in seats.split(",") if s.strip()]
    ok, ng = _set_hold(schedule_id, labels)
    return {
        "schedule_id": schedule_id,
        "held": ok,
        "failed": [{"seat": s, "reason": reason} for s, reason in ng],
        "expires_at_utc": (_utcnow() + timedelta(minutes=HOLD_TTL_MINUTES)).isoformat()
    }

@router.post("/schedules/{schedule_id}/confirm")
def confirm_sold(schedule_id: int, seats: str = Query(..., description="kursi yang di-hold, contoh: A1,B2")):
    """
    Ubah kursi dari HOLD -> SOLD (X). Gagal kalau hold sudah expired atau belum di-hold.
    """
    _sweep_expired_holds()
    labels = [s.strip().upper() for s in seats.split(",") if s.strip()]
    ok, ng = _confirm_sold(schedule_id, labels)
    return {
        "schedule_id": schedule_id,
        "sold": ok,
        "failed": [{"seat": s, "reason": reason} for s, reason in ng],
    }

@router.post("/schedules/{schedule_id}/release")
def release_hold(schedule_id: int, seats: str = Query(..., description="lepas hold manual: A1,B2")):
    """
    Lepas hold secara manual (balik ke available). Buat testing aja.
    """
    _sweep_expired_holds()
    labels = [s.strip().upper() for s in seats.split(",") if s.strip()]
    mat = SEATS_BY_SCHEDULE.get(schedule_id)
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
            HOLDS.pop((schedule_id, label.upper()), None)
            released.append(label.upper())
        else:
            not_released.append({"seat": label.upper(), "reason": "not_on_hold"})
    return {"schedule_id": schedule_id, "released": released, "failed": not_released}
