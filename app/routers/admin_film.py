from fastapi import APIRouter, HTTPException
from app import database
from app.models import Movie

router = APIRouter()

# CREATE - Tambah Film
@router.post("/movies")
def tambah_film(movie_id: str, movie: Movie):
    if movie_id in database.movies:
        raise HTTPException(status_code=400, detail="ID film sudah ada")
    database.movies[movie_id] = movie.dict()
    return {"message": "Film berhasil ditambahkan", "data": database.movies[movie_id]}

# READ - Lihat semua film
@router.get("/movies")
def lihat_semua_film():
    return {"message": "Daftar semua film berhasil diambil", "data": database.movies}

# READ - Lihat satu film
@router.get("/movies/{movie_id}")
def lihat_detail_film(movie_id: str):
    if movie_id not in database.movies:
        raise HTTPException(status_code=404, detail="Film tidak ditemukan")
    return {"message": "Detail film ditemukan", "data": database.movies[movie_id]}

# UPDATE - Perbarui film
@router.put("/movies/{movie_id}")
def perbarui_film(movie_id: str, movie: Movie):
    if movie_id not in database.movies:
        raise HTTPException(status_code=404, detail="Film tidak ditemukan")
    database.movies[movie_id] = movie.dict()
    return {"message": "Data film berhasil diperbarui", "data": database.movies[movie_id]}

# DELETE - Hapus film
@router.delete("/movies/{movie_id}")
def hapus_film(movie_id: str):
    if movie_id not in database.movies:
        raise HTTPException(status_code=404, detail="Film tidak ditemukan")
    del database.movies[movie_id]
    return {"message": f"Film dengan ID {movie_id} berhasil dihapus"}
