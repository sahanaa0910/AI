import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "database.db"))
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
