from flask import Blueprint


# ==========================================================
# Reports Blueprint
# ==========================================================

reports_bp = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports",
)


# ==========================================================
# Import Routes
#
# Import is placed at the bottom to avoid circular imports.
# ==========================================================

from app.reports import routes