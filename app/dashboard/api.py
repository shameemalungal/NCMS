from flask import Blueprint, jsonify

from app.services.dashboard_service import DashboardService

from app.auth.decorators import admin_required


bp = Blueprint(
    "dashboard_api",
    __name__,
    url_prefix="/api/dashboard",
)


@bp.get("/summary")
@admin_required
def summary():

    return jsonify(
        DashboardService.get_summary()
    )