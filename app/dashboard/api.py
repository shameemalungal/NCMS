from flask import Blueprint, jsonify

from app.services.dashboard_service import DashboardService


bp = Blueprint(
    "dashboard_api",
    __name__,
    url_prefix="/api/dashboard",
)


@bp.get("/summary")
def summary():

    return jsonify(
        DashboardService.get_summary()
    )