from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
)

from app.campaign import campaign_bp
from app.campaign.forms import CampaignForm
from app.extensions import db
from app.models import Campaign


@campaign_bp.route("/")
def index():

    search = request.args.get("search", "").strip()

    query = Campaign.query

    if search:
        query = query.filter(
            Campaign.name.ilike(f"%{search}%")
        )

    campaigns = query.order_by(
        Campaign.start_date.desc()
    ).all()

    return render_template(
        "campaign/index.html",
        campaigns=campaigns,
        search=search,
    )


@campaign_bp.route("/add", methods=["GET", "POST"])
def add():

    form = CampaignForm()

    if form.validate_on_submit():

        if Campaign.query.filter_by(code=form.code.data.strip()).first():

            flash(
                "Campaign code already exists.",
                "danger",
            )

            return render_template(
                "campaign/form.html",
                form=form,
                title="New Campaign",
            )

        if form.status.data == "Active":

            Campaign.query.filter_by(
                status="Active"
            ).update(
                {"status": "Draft"}
            )

        campaign = Campaign(
            name=form.name.data.strip(),
            code=form.code.data.strip().upper(),
            description=form.description.data.strip()
            if form.description.data
            else "",
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            status=form.status.data,
        )

        db.session.add(campaign)
        db.session.commit()

        flash(
            "Campaign created successfully.",
            "success",
        )

        return redirect(url_for("campaign.index"))

    return render_template(
        "campaign/form.html",
        form=form,
        title="New Campaign",
    )


@campaign_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    campaign = Campaign.query.get_or_404(id)

    form = CampaignForm(obj=campaign)

    if form.validate_on_submit():

        duplicate = Campaign.query.filter(
            Campaign.code == form.code.data.strip().upper(),
            Campaign.id != campaign.id,
        ).first()

        if duplicate:

            flash(
                "Campaign code already exists.",
                "danger",
            )

            return render_template(
                "campaign/form.html",
                form=form,
                title="Edit Campaign",
            )

        if form.status.data == "Active":

            Campaign.query.filter(
                Campaign.id != campaign.id,
                Campaign.status == "Active",
            ).update(
                {"status": "Draft"}
            )

        campaign.name = form.name.data.strip()
        campaign.code = form.code.data.strip().upper()
        campaign.description = (
            form.description.data.strip()
            if form.description.data
            else ""
        )
        campaign.start_date = form.start_date.data
        campaign.end_date = form.end_date.data
        campaign.status = form.status.data

        db.session.commit()

        flash(
            "Campaign updated successfully.",
            "success",
        )

        return redirect(url_for("campaign.index"))

    return render_template(
        "campaign/form.html",
        form=form,
        title="Edit Campaign",
    )


@campaign_bp.route("/delete/<int:id>", methods=["POST"])
def delete(id):

    campaign = Campaign.query.get_or_404(id)

    db.session.delete(campaign)
    db.session.commit()

    flash(
        "Campaign deleted successfully.",
        "success",
    )

    return redirect(
        url_for("campaign.index")
    )