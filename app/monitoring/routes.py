from flask import Blueprint, render_template

from app.services.monitoring_service import MonitoringService


# ==========================================================
# Monitoring Blueprint
# ==========================================================

monitoring_bp = Blueprint(
    "monitoring",
    __name__,
    url_prefix="/monitoring",
)


# ==========================================================
# District Monitoring
# ==========================================================

@monitoring_bp.route("/")
def index():

    data = MonitoringService.get_dashboard()

    return render_template(
        "monitoring/index.html",
        campaign=data["campaign"],
        summary=data["summary"],
        monitoring=data["monitoring"],
        page_title="District Monitoring",
        page_subtitle="Campaign Progress Monitoring",
    )


# ==========================================================
# Squad-wise Monitoring
# ==========================================================

@monitoring_bp.route("/squads")
def squads():

    data = MonitoringService.get_dashboard()

    campaign = data["campaign"]
    summary = data["summary"]
    monitoring = data["monitoring"]

    # ------------------------------------------------------
    # Flatten Panchayath monitoring into squad rows
    # ------------------------------------------------------

    squad_rows = []

    for row in monitoring:

        # --------------------------------------------------
        # Submitted Squads
        # --------------------------------------------------

        for squad in row.get(
            "submitted_squads",
            []
        ):

            squad_rows.append(
                {
                    "panchayath": (
                        row["panchayath"]
                    ),
                    "squad": squad,
                    "submitted": True,
                }
            )

        # --------------------------------------------------
        # Pending Squads
        # --------------------------------------------------

        for squad in row.get(
            "pending_squads",
            []
        ):

            squad_rows.append(
                {
                    "panchayath": (
                        row["panchayath"]
                    ),
                    "squad": squad,
                    "submitted": False,
                }
            )

    # ------------------------------------------------------
    # Sort by Panchayath and Squad Number
    # ------------------------------------------------------

    squad_rows.sort(
        key=lambda item: (
            item["panchayath"].name.lower(),
            item["squad"].get(
                "squad_no",
                0,
            ),
        )
    )

    return render_template(
        "monitoring/squads.html",
        campaign=campaign,
        summary=summary,
        squad_rows=squad_rows,
        page_title="Squad-wise Monitoring",
        page_subtitle=(
            "Live squad-wise campaign monitoring"
        ),
    )