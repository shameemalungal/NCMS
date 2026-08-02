from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)

from app.extensions import db
from app.models import Campaign
from app.campaign.forms import CampaignForm


campaign_bp = Blueprint(
    "campaign",
    __name__,
    url_prefix="/campaign",
)


# ==========================================================
# Campaign List
# ==========================================================

@campaign_bp.route("/")
def index():

    campaigns = Campaign.query.order_by(
        Campaign.created_at.desc()
    ).all()

    return render_template(
        "campaign/index.html",
        page_title="Campaign Management",
        campaigns=campaigns,
    )


# ==========================================================
# Add Campaign
# ==========================================================

@campaign_bp.route("/add", methods=["GET", "POST"])
def add():

    form = CampaignForm()

    if form.validate_on_submit():

        # Allow only one active campaign
        if form.is_active.data:
            Campaign.query.update({"is_active": False})

        campaign = Campaign(
            name=form.name.data,
            code=form.code.data.upper(),
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            status=form.status.data,
            is_active=form.is_active.data,
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
        page_title="Add Campaign",
        form=form,
        mode="Add",
    )


# ==========================================================
# Edit Campaign
# ==========================================================

@campaign_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    campaign = Campaign.query.get_or_404(id)

    form = CampaignForm(obj=campaign)

    if form.validate_on_submit():

        # Allow only one active campaign
        if form.is_active.data:
            Campaign.query.update({"is_active": False})

        form.populate_obj(campaign)

        campaign.code = campaign.code.upper()

        db.session.commit()

        flash(
            "Campaign updated successfully.",
            "success",
        )

        return redirect(url_for("campaign.index"))

    return render_template(
        "campaign/form.html",
        page_title="Edit Campaign",
        form=form,
        mode="Edit",
    )


# ==========================================================
# Delete Campaign
# ==========================================================

@campaign_bp.route("/delete/<int:id>")
def delete(id):

    campaign = Campaign.query.get_or_404(id)

    db.session.delete(campaign)
    db.session.commit()

    flash(
        "Campaign deleted successfully.",
        "success",
    )

    return redirect(url_for("campaign.index"))