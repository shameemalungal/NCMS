from flask import Blueprint

masterdata_bp = Blueprint(
    "masterdata",
    __name__,
    url_prefix="/masterdata"
)

from app.masterdata import routes