from flask import (
    render_template,
    request,
)

from app.squad import squad_bp
from app.models import Squad, Campaign, Panchayath


@squad_bp.route("/")
def index():

    campaign = request.args.get("campaign", type=int)
    panchayath = request.args.get("panchayath", type=int)
    status = request.args.get("status", "")

    query = Squad.query

    if campaign:
        query = query.filter_by(campaign_id=campaign)

    if panchayath:
        query = query.filter_by(panchayath_id=panchayath)

    if status:

        if status == "Pending":
            query = query.filter(Squad.submission == None)

        elif status == "Submitted":
            query = query.filter(Squad.submission != None)

    squads = (
        query
        .order_by(
            Squad.campaign_id,
            Squad.panchayath_id,
            Squad.squad_no,
        )
        .all()
    )

    campaigns = (
        Campaign.query
        .order_by(Campaign.name)
        .all()
    )

    panchayaths = (
        Panchayath.query
        .order_by(Panchayath.name)
        .all()
    )

    return render_template(
        "squad/index.html",
        squads=squads,
        campaigns=campaigns,
        panchayaths=panchayaths,
        selected_campaign=campaign,
        selected_panchayath=panchayath,
        selected_status=status,
    )