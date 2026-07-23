from flask import render_template

from app.dashboard import dashboard_bp
from app.models import Campaign, Panchayath, Squad, Submission


@dashboard_bp.route("/")
def dashboard():

    campaigns = Campaign.query.count()

    panchayaths = Panchayath.query.count()

    squads = Squad.query.count()

    submitted = Submission.query.count()

    pending = Squad.query.filter_by(status="Pending").count()

    completed = Squad.query.filter_by(status="Completed").count()

    population = sum(
        p.population or 0
        for p in Panchayath.query.all()
    )

    completion = 0

    if squads:
        completion = round((submitted / squads) * 100, 1)

    return render_template(
        "dashboard.html",

        campaigns=campaigns,
        panchayaths=panchayaths,
        squads=squads,
        submitted=submitted,
        pending=pending,
        completed=completed,
        population=population,
        completion=completion
    )