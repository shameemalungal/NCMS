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
# STEP 1
# Select Panchayath & Squad
# ==========================================================

@submission_bp.route("/", methods=["GET"])
def index():

    campaign = Campaign.query.filter_by(
        is_active=True
    ).first()

    if campaign is None:
        return render_template(
            "submission/no_campaign.html",
            page_label="NCMS Submission",
            page_title="No Active Campaign",
            page_subtitle="No campaign is currently active",
        )

    panchayaths = (
        Panchayath.query.filter_by(
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

    squads = (
        Squad.query.filter_by(
            panchayath_id=panchayath_id
        )
        .order_by(Squad.squad_no)
        .all()
    )

    return jsonify([
        {
            "id": squad.id,
            "squad_no": squad.squad_no,
            "submitted": squad.submission is not None,
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

    squad = Squad.query.get_or_404(squad_id)

    members = []

    for member in squad.members:

        members.append(
            {
                "name": member.member_name,
                "office": member.office,
                "pashudhan_id": member.pashudhan_id,
            }
        )

    return jsonify(
        {
            "submitted": squad.submission is not None,

            "campaign": squad.campaign.name,

            "campaign_code": squad.campaign.code,

            "panchayath": squad.panchayath.name,

            "squad_no": squad.squad_no,

            "target": squad.target,

            "days": squad.squad_days,

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

    squad = Squad.query.get_or_404(squad_id)

    # ------------------------------------------------------
    # Duplicate protection before showing the form
    # ------------------------------------------------------

    if SubmissionService.squad_already_submitted(
        squad.id
    ):

        flash(
            "This squad has already submitted the report.",
            "warning",
        )

        return render_template(
            "submission/already_submitted.html",
            squad=squad,
            submission=squad.submission,
            page_label="NCMS Submission",
            page_title="Already Submitted",
            page_subtitle=(
                "This squad has already completed its submission"
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
            page_subtitle="Submit Vaccination Report",
        )

    # ------------------------------------------------------
    # POST
    # ------------------------------------------------------

    if form.validate_on_submit():

        try:

            submission = (
                SubmissionService.create_submission(
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
                "This squad has already submitted the report.",
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
                f"Unable to save submission: {ex}",
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
        page_subtitle="Submit Vaccination Report",
    )


# ==========================================================
# Success
# ==========================================================

@submission_bp.route(
    "/success/<int:squad_id>"
)
def success(squad_id):

    squad = Squad.query.get_or_404(squad_id)

    if squad.submission is None:

        return redirect(
            url_for("submission.index")
        )

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