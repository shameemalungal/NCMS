from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    session,
)

from app.services.monitoring_service import MonitoringService
from app.services.resubmission_service import ResubmissionService

from app.auth.decorators import (
    require_permission,
    get_current_user,
)


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
@require_permission("monitoring.view")
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
@require_permission("monitoring.squads.view")
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
                    "panchayath": row["panchayath"],
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
                    "panchayath": row["panchayath"],
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


# ==========================================================
# Allow Squad Re-submission
# ==========================================================

@monitoring_bp.route(
    "/squads/<int:squad_id>/allow-resubmission",
    methods=["POST"],
)
@require_permission("monitoring.resubmission")
def allow_resubmission(squad_id):

    user = get_current_user()

    username = (
        user.username
        if user
        else "Administrator"
    )

    result = (
        ResubmissionService.allow_resubmission(
            squad_id=squad_id,
            username=username,
        )
    )

    if result["success"]:

        flash(
            result["message"],
            "success",
        )

    else:

        flash(
            result["message"],
            "danger",
        )

    return redirect(
        url_for(
            "monitoring.squads"
        )
    )
# ==========================================================
# Submission History
# ==========================================================

@monitoring_bp.route("/submission-history")
@require_permission("monitoring.history.view")
def submission_history():

    history = (
        ResubmissionService
        .get_submission_history()
    )

    return render_template(
        "monitoring/submission_history.html",
        history=history,
        page_title="Submission History",
        page_subtitle=(
            "Archived submissions from "
            "re-submission workflow"
        ),
    )