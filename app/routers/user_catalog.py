from sched import scheduler
from fastapi import APIRouter, HTTPException
from app.routers.admin_film import list_film
from app.routers.admin_jadwal import list_jadwal

router = APIRouter(prefix="/user/catalog", tags=["User - Catalog"])

@router.get("/movies")
def lihat_daftar_film_dan_jadwal():
    if not list_film:
        raise HTTPException(status_code=404, detail="Belum ada film")
    katalog = []
    for film in list_film:
        film_jadwal = [
            {"studio": s["studio_name"], "time": s["time"]}
            for s in scheduler if s["movie_id"] == film["id"]
        ]
        katalog.append({
            "title": film["title"],
            "duration": film["duration"],
            "price": film["price"],
            "showtimes": film_jadwal
        })
    return katalog
