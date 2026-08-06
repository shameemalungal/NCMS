from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)

from app.auth.decorators import admin_required
from app.campaign.forms import CampaignForm
from app.extensions import db
from app.models import Campaign


campaign_bp = Blueprint(
    "campaign",
    __name__,
    url_prefix="/campaign",
)


# ==========================================================
# Campaign List
# ==========================================================

@campaign_bp.route("/")
@admin_required
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

@campaign_bp.route(
    "/add",
    methods=["GET", "POST"],
)
@admin_required
def add():

    form = CampaignForm()

    if form.validate_on_submit():

        # --------------------------------------------------
        # Allow only one active campaign
        # --------------------------------------------------

        if form.is_active.data:

            Campaign.query.update(
                {
                    "is_active": False
                }
            )

        # --------------------------------------------------
        # Create Campaign
        # --------------------------------------------------

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

        return redirect(
            url_for("campaign.index")
        )

    return render_template(
        "campaign/form.html",
        page_title="Add Campaign",
        form=form,
        mode="Add",
    )


# ==========================================================
# Edit Campaign
# ==========================================================

@campaign_bp.route(
    "/edit/<int:id>",
    methods=["GET", "POST"],
)
@admin_required
def edit(id):

    campaign = Campaign.query.get_or_404(id)

    form = CampaignForm(
        obj=campaign
    )

    if form.validate_on_submit():

        # --------------------------------------------------
        # Allow only one active campaign
        # --------------------------------------------------

        if form.is_active.data:

            Campaign.query.update(
                {
                    "is_active": False
                }
            )

        # --------------------------------------------------
        # Update Campaign
        # --------------------------------------------------

        form.populate_obj(
            campaign
        )

        campaign.code = (
            campaign.code.upper()
        )

        db.session.commit()

        flash(
            "Campaign updated successfully.",
            "success",
        )

        return redirect(
            url_for("campaign.index")
        )

    return render_template(
        "campaign/form.html",
        page_title="Edit Campaign",
        form=form,
        mode="Edit",
    )


# ==========================================================
# Delete Campaign
# ==========================================================

@campaign_bp.route(
    "/delete/<int:id>",
    methods=["POST"],
)
@admin_required
def delete(id):

    campaign = (
        Campaign.query.get_or_404(id)
    )

    # ------------------------------------------------------
    # Protect Active Campaign
    # ------------------------------------------------------

    if campaign.is_active:

        flash(
            (
                "The active campaign cannot be deleted. "
                "Deactivate it before attempting deletion."
            ),
            "warning",
        )

        return redirect(
            url_for("campaign.index")
        )

    # ------------------------------------------------------
    # Delete Inactive Campaign
    # ------------------------------------------------------

    db.session.delete(
        campaign
    )

    db.session.commit()

    flash(
        "Campaign deleted successfully.",
        "success",
    )

    return redirect(
        url_for("campaign.index")
    )