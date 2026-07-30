from app.dashboard.services import DashboardService


@bp.route("/")
def index():

    dashboard = DashboardService.summary()

    submissions = DashboardService.recent()

    return render_template(

        "dashboard/index.html",

        dashboard=dashboard,

        submissions=submissions

    )
@bp.get("/api/summary")
def api_summary():

    return DashboardService.summary()