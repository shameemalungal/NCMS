from flask import (
    render_template,
    request,
    jsonify,
    flash,
    redirect,
    url_for,
)

from app.models import (
    Campaign,
    Panchayath,
    Squad,
)

from app.submission import submission_bp
from app.submission.forms import SubmissionForm

from app.services.submission_service import (
    SubmissionService,
    DuplicateSubmissionError,
)


# ==========================================================
# Helper
# Active Campaign
# ==========================================================

def get_active_campaign():
    """
    Return the currently active campaign.
    """

    return (
        Campaign.query
        .filter_by(is_active=True)
        .first()
    )


# ==========================================================
# Helper
# Closed Submission Page
# ==========================================================

def render_submissions_closed(campaign):

    return render_template(
        "submission/submissions_closed.html",
        campaign=campaign,
        page_label="NCMS Submission",
        page_title="Submissions Closed",
        page_subtitle=(
            "Public submissions are currently closed"
        ),
    )


# ==========================================================
# STEP 1
# Select Panchayath & Squad
# ==========================================================

@submission_bp.route("/", methods=["GET"])
def index():

    campaign = get_active_campaign()

    # ------------------------------------------------------
    # No active campaign
    # ------------------------------------------------------

    if campaign is None:

        return render_template(
            "submission/no_campaign.html",
            page_label="NCMS Submission",
            page_title="No Active Campaign",
            page_subtitle="No campaign is currently active",
        )

    # ------------------------------------------------------
    # Public submissions closed
    # ------------------------------------------------------

    if not campaign.submissions_open:

        return render_submissions_closed(
            campaign
        )

    # ------------------------------------------------------
    # Panchayaths
    # ------------------------------------------------------

    panchayaths = (
        Panchayath.query
        .filter_by(
            campaign_id=campaign.id
        )
        .order_by(Panchayath.name)
        .all()
    )

    return render_template(
        "submission/select_squad.html",
        campaign=campaign,
        panchayaths=panchayaths,
        page_label="NCMS Submission",
        page_title="Select Squad",
        page_subtitle="Choose Panchayath and Squad",
    )


# ==========================================================
# AJAX
# Return Squads of Panchayath
# ==========================================================

@submission_bp.route(
    "/api/squads/<int:panchayath_id>"
)
def get_squads(panchayath_id):

    # ------------------------------------------------------
    # Panchayath
    # ------------------------------------------------------

    panchayath = Panchayath.query.get_or_404(
        panchayath_id
    )

    campaign = panchayath.campaign

    # ------------------------------------------------------
    # Campaign must be active
    # ------------------------------------------------------

    if not campaign.is_active:

        return jsonify(
            {
                "error": (
                    "This campaign is not active."
                )
            }
        ), 403

    # ------------------------------------------------------
    # Public submissions must be open
    # ------------------------------------------------------

    if not campaign.submissions_open:

        return jsonify(
            {
                "error": (
                    "Public submissions are currently closed."
                )
            }
        ), 403

    # ------------------------------------------------------
    # Squads
    # ------------------------------------------------------

    squads = (
        Squad.query
        .filter_by(
            panchayath_id=panchayath.id
        )
        .order_by(Squad.squad_no)
        .all()
    )

    return jsonify([
        {
            "id": squad.id,
            "squad_no": squad.squad_no,
            "submitted": (
                squad.submission is not None
            ),
        }
        for squad in squads
    ])


# ==========================================================
# AJAX
# Squad Details
# ==========================================================

@submission_bp.route(
    "/api/squad/<int:squad_id>"
)
def squad_details(squad_id):

    squad = Squad.query.get_or_404(
        squad_id
    )

    campaign = squad.campaign

    # ------------------------------------------------------
    # Campaign must be active
    # ------------------------------------------------------

    if not campaign.is_active:

        return jsonify(
            {
                "error": (
                    "This campaign is not active."
                )
            }
        ), 403

    # ------------------------------------------------------
    # Public submissions must be open
    # ------------------------------------------------------

    if not campaign.submissions_open:

        return jsonify(
            {
                "error": (
                    "Public submissions are currently closed."
                )
            }
        ), 403

    # ------------------------------------------------------
    # Members
    # ------------------------------------------------------

    members = []

    for member in squad.members:

        members.append(
            {
                "name": member.member_name,
                "office": member.office,
                "pashudhan_id": (
                    member.pashudhan_id
                ),
            }
        )

    return jsonify(
        {
            "submitted": (
                squad.submission is not None
            ),

            "campaign": (
                squad.campaign.name
            ),

            "campaign_code": (
                squad.campaign.code
            ),

            "panchayath": (
                squad.panchayath.name
            ),

            "squad_no": (
                squad.squad_no
            ),

            "target": (
                squad.target
            ),

            "days": (
                squad.squad_days
            ),

            "members": members,
        }
    )


# ==========================================================
# Open / Submit Form
# ==========================================================

@submission_bp.route(
    "/form/<int:squad_id>",
    methods=["GET", "POST"],
)
def form(squad_id):

    squad = Squad.query.get_or_404(
        squad_id
    )

    campaign = squad.campaign

    # ------------------------------------------------------
    # Campaign must still be active
    # ------------------------------------------------------

    if not campaign.is_active:

        flash(
            (
                "This campaign is no longer active."
            ),
            "warning",
        )

        return redirect(
            url_for("submission.index")
        )

    # ------------------------------------------------------
    # CRITICAL:
    # Server-side submission control
    #
    # This runs BEFORE form processing, therefore both
    # direct GET access and direct POST attempts are blocked.
    # ------------------------------------------------------

    if not campaign.submissions_open:

        return render_submissions_closed(
            campaign
        )

    # ------------------------------------------------------
    # Duplicate protection before showing the form
    # ------------------------------------------------------

    if SubmissionService.squad_already_submitted(
        squad.id
    ):

        flash(
            (
                "This squad has already submitted "
                "the report."
            ),
            "warning",
        )

        return render_template(
            "submission/already_submitted.html",
            squad=squad,
            submission=squad.submission,
            page_label="NCMS Submission",
            page_title="Already Submitted",
            page_subtitle=(
                "This squad has already completed "
                "its submission"
            ),
        )

    form = SubmissionForm()

    # ------------------------------------------------------
    # GET
    # ------------------------------------------------------

    if request.method == "GET":

        return render_template(
            "submission/form.html",
            squad=squad,
            members=squad.members,
            form=form,
            page_label="NCMS Submission",
            page_title="New Submission",
            page_subtitle=(
                "Submit Vaccination Report"
            ),
        )

    # ------------------------------------------------------
    # POST
    # ------------------------------------------------------

    if form.validate_on_submit():

        # --------------------------------------------------
        # Recheck immediately before database write.
        #
        # This makes the intention explicit even though
        # the campaign was already checked above.
        # --------------------------------------------------

        if not campaign.submissions_open:

            return render_submissions_closed(
                campaign
            )

        try:

            submission = (
                SubmissionService
                .create_submission(
                    squad=squad,
                    form=form,
                    source="Web",
                )
            )

            flash(
                (
                    "Submission saved successfully. "
                    f"Reference: "
                    f"{submission.submission_token}"
                ),
                "success",
            )

            return redirect(
                url_for(
                    "submission.success",
                    squad_id=squad.id,
                )
            )

        except DuplicateSubmissionError:

            flash(
                (
                    "This squad has already "
                    "submitted the report."
                ),
                "warning",
            )

            return redirect(
                url_for(
                    "submission.form",
                    squad_id=squad.id,
                )
            )

        except Exception as ex:

            from app.extensions import db

            db.session.rollback()

            flash(
                (
                    "Unable to save submission: "
                    f"{ex}"
                ),
                "danger",
            )

    # ------------------------------------------------------
    # Validation failed
    # ------------------------------------------------------

    return render_template(
        "submission/form.html",
        squad=squad,
        members=squad.members,
        form=form,
        page_label="NCMS Submission",
        page_title="New Submission",
        page_subtitle=(
            "Submit Vaccination Report"
        ),
    )


# ==========================================================
# Success
# ==========================================================

@submission_bp.route(
    "/success/<int:squad_id>"
)
def success(squad_id):

    squad = Squad.query.get_or_404(
        squad_id
    )

    if squad.submission is None:

        return redirect(
            url_for("submission.index")
        )

    # ------------------------------------------------------
    # Success pages remain accessible even if submissions
    # have subsequently been closed.
    #
    # This allows a user to retain/view confirmation of an
    # already completed submission.
    # ------------------------------------------------------

    return render_template(
        "submission/success.html",
        squad=squad,
        submission=squad.submission,
        page_label="NCMS Submission",
        page_title="Submission Successful",
        page_subtitle=(
            "Vaccination report received successfully"
        ),
    )