# app/main.py
from fastapi import FastAPI
from .routers.user_catalog import router as user_router  # <- pakai titik

app = FastAPI(title="Movie Booking System")
app.include_router(user_router)

@app.get("/")
def home():
    return {"message": "Movie Booking API — Person 3 endpoints active!"}
