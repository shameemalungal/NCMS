from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = "change-this-to-a-random-secret-key"

    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{BASE_DIR / 'database' / 'ncms.db'}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False