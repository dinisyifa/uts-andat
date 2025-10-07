from fastapi import APIRouter, HTTPException
from app.models import Movie

router = APIRouter()

# Simulasi "database" sementara dengan list di memori
list_film = []

# CREATE - Tambah Film
@router.post("/movies")
def tambah_film(movie: Movie):
    # Cek apakah ID film sudah ada
    for f in list_film:
        if f["id"] == movie.id:
            raise HTTPException(status_code=400, detail="ID film sudah ada")
    list_film.append(movie.dict())
    return {"message": "Film berhasil ditambahkan", "data": movie}

# READ - Lihat semua film
@router.get("/movies")
def lihat_semua_film():
    if not list_film:
        raise HTTPException(status_code=404, detail="Belum ada film yang terdaftar")
    return {"message": "Daftar semua film berhasil diambil", "data": list_film}

# READ - Lihat satu film
@router.get("/movies/{movie_id}")
def lihat_detail_film(movie_id: str):
    for film in list_film:
        if film["id"] == movie_id:
            return {"message": "Detail film ditemukan", "data": film}
    raise HTTPException(status_code=404, detail="Film tidak ditemukan")

# UPDATE - Perbarui film
@router.put("/movies/{movie_id}")
def perbarui_film(movie_id: str, movie: Movie):
    for idx, film in enumerate(list_film):
        if film["id"] == movie_id:
            list_film[idx] = movie.dict()
            return {"message": "Data film berhasil diperbarui", "data": movie}
    raise HTTPException(status_code=404, detail="Film tidak ditemukan")

# DELETE - Hapus film
@router.delete("/movies/{movie_id}")
def hapus_film(movie_id: str):
    for idx, film in enumerate(list_film):
        if film["id"] == movie_id:
            del list_film[idx]
            return {"message": f"Film dengan ID {movie_id} berhasil dihapus"}
    raise HTTPException(status_code=404, detail="Film tidak ditemukan")
