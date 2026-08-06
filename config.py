import os
from pathlib import Path


# ==========================================================
# Base Directory
# ==========================================================

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
    # Administrator Authentication
    # ======================================================

    ADMIN_USERNAME = os.environ.get(
        "NCMS_ADMIN_USERNAME",
        "admin",
    )

    ADMIN_PASSWORD = os.environ.get(
        "NCMS_ADMIN_PASSWORD", 
        "admin"
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

    # Prevent JavaScript from accessing the session cookie.
    SESSION_COOKIE_HTTPONLY = True

    # Helps protect against cross-site request attacks while
    # allowing normal navigation within NCMS.
    SESSION_COOKIE_SAMESITE = "Lax"

    # Keep False while NCMS is running locally using HTTP.
    #
    # Change to True when NCMS is deployed behind HTTPS.
    SESSION_COOKIE_SECURE = False