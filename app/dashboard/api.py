from flask import Blueprint, jsonify

from app.services.dashboard_service import DashboardService

from app.auth.decorators import require_permission


bp = Blueprint(
    "dashboard_api",
    __name__,
    url_prefix="/api/dashboard",
)


@bp.get("/summary")
@require_permission("monitoring.view")
def summary():

    return jsonify(
        DashboardService.get_summary()
    )