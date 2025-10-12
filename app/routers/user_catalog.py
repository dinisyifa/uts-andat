# file: app/routers/user_catalog.py (Versi Perbaikan & Sinkronisasi)

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, List, Any

# --- Impor Sumber Data Utama ---
from app.routers.admin_film import list_film
from app.routers.admin_jadwal import raw_jadwal_template

router = APIRouter()

# ======================================================
# LOGIKA UNTUK MENAHAN KURSI (SEAT HOLDING)
# ======================================================
HOLD_TTL_MINUTES = 30
HOLDS: Dict[Tuple[str, str], datetime] = {}

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

def _find_schedule(schedule_id: str) -> Optional[Dict]:
    return next((s for s in raw_jadwal_template if s.get("id") == schedule_id), None)

def _sweep_expired_holds():
    now = _utcnow()
    expired_keys = [key for key, exp_at in HOLDS.items() if exp_at <= now]
    
    for sched_id, seat_label in expired_keys:
        schedule = _find_schedule(sched_id)
        if schedule and schedule.get("seats", {}).get(seat_label, {}).get("status") == "held":
            schedule["seats"][seat_label]["status"] = "available"
        HOLDS.pop((sched_id, seat_label), None)

def _set_hold(schedule: Dict, labels: List[str]) -> Tuple[List[str], List[Tuple[str, str]]]:
    ok, ng = [], []
    expires_at = _utcnow() + timedelta(minutes=HOLD_TTL_MINUTES)
    
    for label in labels:
        seat = schedule.get("seats", {}).get(label)
        if not seat:
            ng.append((label, "invalid_seat"))
            continue
        
        if seat.get("status") == "available":
            seat["status"] = "held"
            HOLDS[(schedule["id"], label)] = expires_at
            ok.append(label)
        else:
            ng.append((label, "not_available"))
    return ok, ng

# ======================================================
# ENDPOINTS (USER - KATALOG)
# ======================================================

@router.get("/movies/now-playing")
def get_now_playing_movies():
    # ... (logika endpoint ini bisa tetap sama) ...
    if not list_film:
        raise HTTPException(status_code=404, detail="Saat ini belum ada film yang terdaftar.")
    return {"data": list_film}

@router.get("/movies/{movie_id}/details")
def get_movie_details_and_schedules(movie_id: str):
    # ... (logika endpoint ini bisa tetap sama) ...
    movie = next((f for f in list_film if f.get("id") == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Film tidak ditemukan.")
    movie_schedules = [s for s in raw_jadwal_template if s.get("movie_id") == movie_id]
    return {"movie_details": movie, "schedules": movie_schedules}

@router.get("/schedules/{schedule_id}/seats")
def get_seat_map(schedule_id: str):
    _sweep_expired_holds()
    schedule = _find_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Jadwal tidak ditemukan.")
    return {"schedule_info": schedule, "seats": schedule.get("seats")}

@router.post("/schedules/{schedule_id}/hold")
def hold_seats(schedule_id: str, seats_to_hold: List[str]):
    _sweep_expired_holds()
    schedule = _find_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Jadwal tidak ditemukan.")
    ok, ng = _set_hold(schedule, seats_to_hold)
    if not ok:
        raise HTTPException(status_code=400, detail={"message": "Gagal menahan kursi", "failed_seats": ng})
    return {"held_seats": ok, "failed_seats": ng, "expires_at": (_utcnow() + timedelta(minutes=HOLD_TTL_MINUTES)).isoformat()}
