from flask import Blueprint

campaign_bp = Blueprint(
    "campaign",
    __name__,
    url_prefix="/campaigns",
)

from app.campaign import routes