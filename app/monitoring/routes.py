from flask import Blueprint
from flask import render_template

from app.services.monitoring_service import (
    MonitoringService,
)

monitoring_bp = Blueprint(
    "monitoring",
    __name__,
    url_prefix="/monitoring"
)


@monitoring_bp.route("/")
def index():

    data = MonitoringService.get_dashboard()

    return render_template(

        "monitoring/index.html",

        campaign=data["campaign"],

        monitoring=data["monitoring"],

        page_label="NCMS Monitoring",

        page_title="District Monitoring",

        page_subtitle="Real-time Campaign Progress",

    )