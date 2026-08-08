import os
from pathlib import Path


# ==========================================================
# Base Directory
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:

    # ======================================================
    # Environment
    # ======================================================

    ENVIRONMENT = os.environ.get(
        "NCMS_ENVIRONMENT",
        "development",
    ).strip().lower()

    IS_PRODUCTION = ENVIRONMENT == "production"

    # ======================================================
    # Security
    # ======================================================

    SECRET_KEY = os.environ.get("NCMS_SECRET_KEY")

    if not SECRET_KEY:
        if IS_PRODUCTION:
            raise RuntimeError(
                "NCMS_SECRET_KEY must be set in production."
            )
        SECRET_KEY = "ncms-development-only-key"

    # ======================================================
    # Administrator Authentication
    # ======================================================

    ADMIN_USERNAME = os.environ.get(
        "NCMS_ADMIN_USERNAME",
        "admin",
    )

    ADMIN_PASSWORD = os.environ.get(
        "NCMS_ADMIN_PASSWORD"
    )

    if not ADMIN_PASSWORD:
        if IS_PRODUCTION:
            raise RuntimeError(
                "NCMS_ADMIN_PASSWORD must be set in production."
            )
        ADMIN_PASSWORD = "admin"

    # ======================================================
    # Database
    # ======================================================

    DEFAULT_DATABASE_URI = (
        f"sqlite:///{BASE_DIR / 'database' / 'ncms.db'}"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        DEFAULT_DATABASE_URI,
    ).replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ======================================================
    # Session Security
    # ======================================================

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get(
        "NCMS_SESSION_COOKIE_SECURE",
        "false",
    ).lower() == "true"

    # ======================================================
    # Request / Host Security
    # ======================================================

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    TRUSTED_HOSTS = [
        host.strip()
        for host in os.environ.get(
            "NCMS_TRUSTED_HOSTS",
            "",
        ).split(",")
        if host.strip()
    ] or None
