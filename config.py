import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:

    # ======================================================
    # Security
    # ======================================================

    SECRET_KEY = os.environ.get(
        "NCMS_SECRET_KEY",
        "ncms-development-only-key",
    )

    # ======================================================
    # Database
    # ======================================================

    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{BASE_DIR / 'database' / 'ncms.db'}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ======================================================
    # Session Security
    # ======================================================

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Keep False during local HTTP development.
    # Production HTTPS deployment will change this to True.
    SESSION_COOKIE_SECURE = False