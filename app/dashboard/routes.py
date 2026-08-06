from flask import render_template

from app.dashboard import dashboard_bp
from app.services.dashboard_service import DashboardService
from app.auth.decorators import admin_required


@dashboard_bp.route("/")
@admin_required
def index():

    dashboard = DashboardService.get_dashboard()

    return render_template(
        "dashboard/index.html",
        dashboard=dashboard,
        submissions=dashboard["recent_submissions"],
        page_label="NCMS Dashboard",
        page_title="Dashboard",
        page_subtitle="NADCP Campaign Management System",
    )