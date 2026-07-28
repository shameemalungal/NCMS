from flask import Blueprint, render_template

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/"
)


@dashboard_bp.route("/")
def index():

    dashboard = {
        "campaign": "NADCP Phase IX",
        "status": "Active",
        "days_remaining": 124,
        "campaigns": 1,
        "squads": 0,
        "submitted": 0,
        "vaccinations": 0,
        "achievement": 0,
    }

    return render_template(
        "dashboard/index.html",
        page_title="Dashboard",
        dashboard=dashboard,
    )