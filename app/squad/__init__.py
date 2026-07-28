from flask import Blueprint

squad_bp = Blueprint(
    "squad",
    __name__,
    url_prefix="/squads",
)

from app.squad import routes