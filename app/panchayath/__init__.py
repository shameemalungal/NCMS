from flask import Blueprint

panchayath_bp = Blueprint(
    "panchayath",
    __name__,
    url_prefix="/panchayaths",
)

from app.panchayath import routes