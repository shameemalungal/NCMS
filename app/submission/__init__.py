from flask import Blueprint

submission_bp = Blueprint(
    "submission",
    __name__,
    url_prefix="/submit"
)

from app.submission import routes