from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from sqlalchemy import or_

from app.extensions import db

from app.models import (
    Campaign,
    Panchayath,
    Squad,
    SquadMember,
)

from app.settings import settings_bp


# ==========================================================
# Settings Dashboard
# ==========================================================

@settings_bp.route("/")
def index():

    # ------------------------------------------------------
    # Active Campaign
    # ------------------------------------------------------

    campaign = Campaign.query.filter_by(
        is_active=True
    ).first()

    # ------------------------------------------------------
    # Render Settings
    # ------------------------------------------------------

    return render_template(
        "settings/index.html",
        campaign=campaign,
        page_label="NCMS Administration",
        page_title="Settings",
        page_subtitle=(
            "Application configuration and "
            "public submission controls"
        ),
    )


# ==========================================================
# Public Submission Control
# ==========================================================

@settings_bp.route(
    "/submission-control",
    methods=["POST"],
)
def submission_control():

    # ------------------------------------------------------
    # Active Campaign
    # ------------------------------------------------------

    campaign = Campaign.query.filter_by(
        is_active=True
    ).first()

    if campaign is None:

        flash(
            "No active campaign is available.",
            "warning",
        )

        return redirect(
            url_for("settings.index")
        )

    # ------------------------------------------------------
    # Requested Action
    # ------------------------------------------------------

    action = (
        request.form.get(
            "action",
            ""
        )
        .strip()
        .lower()
    )

    # ------------------------------------------------------
    # Open Public Submissions
    # ------------------------------------------------------

    if action == "open":

        campaign.submissions_open = True

        db.session.commit()

        flash(
            "Public submissions opened successfully.",
            "success",
        )

    # ------------------------------------------------------
    # Close Public Submissions
    # ------------------------------------------------------

    elif action == "close":

        campaign.submissions_open = False

        db.session.commit()

        flash(
            "Public submissions closed successfully.",
            "success",
        )

    # ------------------------------------------------------
    # Invalid Action
    # ------------------------------------------------------

    else:

        flash(
            "Invalid submission control action.",
            "danger",
        )

    return redirect(
        url_for("settings.index")
    )


# ==========================================================
# Squad & Member Management
# ==========================================================

@settings_bp.route("/squads")
def squads():

    # ------------------------------------------------------
    # Active Campaign
    # ------------------------------------------------------

    campaign = Campaign.query.filter_by(
        is_active=True
    ).first()

    # ------------------------------------------------------
    # No Active Campaign
    # ------------------------------------------------------

    if campaign is None:

        return render_template(
            "settings/squads.html",
            campaign=None,
            panchayaths=[],
            squads=[],
            selected_panchayath_id=None,
            search_query="",
            page_label="NCMS Administration",
            page_title="Squad & Member Management",
            page_subtitle=(
                "Manage squad and member master data"
            ),
        )

    # ------------------------------------------------------
    # Panchayaths
    # ------------------------------------------------------

    panchayaths = (
        Panchayath.query
        .filter_by(
            campaign_id=campaign.id
        )
        .order_by(
            Panchayath.name
        )
        .all()
    )

    # ------------------------------------------------------
    # Filters
    # ------------------------------------------------------

    selected_panchayath_id = request.args.get(
        "panchayath_id",
        type=int,
    )

    search_query = (
        request.args.get(
            "search",
            ""
        )
        .strip()
    )

    # ------------------------------------------------------
    # Base Squad Query
    # ------------------------------------------------------

    squad_query = (
        Squad.query
        .filter(
            Squad.campaign_id == campaign.id
        )
    )

    # ------------------------------------------------------
    # Panchayath Filter
    # ------------------------------------------------------

    if selected_panchayath_id:

        squad_query = squad_query.filter(
            Squad.panchayath_id
            == selected_panchayath_id
        )

    # ------------------------------------------------------
    # Search
    # ------------------------------------------------------

    if search_query:

        search_pattern = (
            f"%{search_query}%"
        )

        squad_query = (
            squad_query
            .outerjoin(
                Panchayath,
                Squad.panchayath_id
                == Panchayath.id,
            )
            .outerjoin(
                SquadMember,
                SquadMember.squad_id
                == Squad.id,
            )
            .filter(
                or_(
                    db.cast(
                        Squad.squad_no,
                        db.String,
                    ).ilike(
                        search_pattern
                    ),

                    Panchayath.name.ilike(
                        search_pattern
                    ),

                    SquadMember.member_name.ilike(
                        search_pattern
                    ),

                    SquadMember.designation.ilike(
                        search_pattern
                    ),

                    SquadMember.office.ilike(
                        search_pattern
                    ),

                    SquadMember.pashudhan_id.ilike(
                        search_pattern
                    ),
                )
            )
            .distinct()
        )

    # ------------------------------------------------------
    # Result
    # ------------------------------------------------------

    squads = (
        squad_query
        .order_by(
            Squad.squad_no
        )
        .all()
    )

    # ------------------------------------------------------
    # Render
    # ------------------------------------------------------

    return render_template(
        "settings/squads.html",
        campaign=campaign,
        panchayaths=panchayaths,
        squads=squads,
        selected_panchayath_id=(
            selected_panchayath_id
        ),
        search_query=search_query,
        page_label="NCMS Administration",
        page_title="Squad & Member Management",
        page_subtitle=(
            "Manage squad and member master data"
        ),
    )


# ==========================================================
# Edit Squad & Members
# ==========================================================

@settings_bp.route(
    "/squads/<int:squad_id>/edit",
    methods=["GET", "POST"],
)
def edit_squad(squad_id):

    # ------------------------------------------------------
    # Active Campaign
    # ------------------------------------------------------

    campaign = Campaign.query.filter_by(
        is_active=True
    ).first()

    if campaign is None:

        flash(
            "No active campaign is available.",
            "warning",
        )

        return redirect(
            url_for("settings.index")
        )

    # ------------------------------------------------------
    # Squad
    # ------------------------------------------------------

    squad = Squad.query.filter_by(
        id=squad_id,
        campaign_id=campaign.id,
    ).first_or_404()

    # ------------------------------------------------------
    # Panchayaths
    # ------------------------------------------------------

    panchayaths = (
        Panchayath.query
        .filter_by(
            campaign_id=campaign.id
        )
        .order_by(
            Panchayath.name
        )
        .all()
    )

    # ------------------------------------------------------
    # Save Changes
    # ------------------------------------------------------

    if request.method == "POST":

        try:

            # --------------------------------------------------
            # Squad Number
            # --------------------------------------------------

            squad_no_raw = (
                request.form.get(
                    "squad_no",
                    ""
                )
                .strip()
            )

            if not squad_no_raw:

                flash(
                    "Squad number is required.",
                    "danger",
                )

                return redirect(
                    url_for(
                        "settings.edit_squad",
                        squad_id=squad.id,
                    )
                )

            try:

                new_squad_no = int(
                    squad_no_raw
                )

            except ValueError:

                flash(
                    "Squad number must be a valid number.",
                    "danger",
                )

                return redirect(
                    url_for(
                        "settings.edit_squad",
                        squad_id=squad.id,
                    )
                )

            if new_squad_no <= 0:

                flash(
                    "Squad number must be greater than zero.",
                    "danger",
                )

                return redirect(
                    url_for(
                        "settings.edit_squad",
                        squad_id=squad.id,
                    )
                )

            # --------------------------------------------------
            # Duplicate Squad Number Protection
            # --------------------------------------------------

            duplicate_squad = (
                Squad.query
                .filter(
                    Squad.campaign_id
                    == campaign.id,

                    Squad.squad_no
                    == new_squad_no,

                    Squad.id
                    != squad.id,
                )
                .first()
            )

            if duplicate_squad:

                flash(
                    (
                        f"Squad {new_squad_no} already exists "
                        "in the active campaign."
                    ),
                    "danger",
                )

                return redirect(
                    url_for(
                        "settings.edit_squad",
                        squad_id=squad.id,
                    )
                )

            # --------------------------------------------------
            # Panchayath
            # --------------------------------------------------

            panchayath_id = request.form.get(
                "panchayath_id",
                type=int,
            )

            panchayath = (
                Panchayath.query
                .filter_by(
                    id=panchayath_id,
                    campaign_id=campaign.id,
                )
                .first()
            )

            if panchayath is None:

                flash(
                    "Please select a valid Panchayath.",
                    "danger",
                )

                return redirect(
                    url_for(
                        "settings.edit_squad",
                        squad_id=squad.id,
                    )
                )

            # --------------------------------------------------
            # Days Allotted
            # --------------------------------------------------

            squad_days_raw = (
                request.form.get(
                    "squad_days",
                    "0"
                )
                .strip()
            )

            try:

                squad_days = int(
                    squad_days_raw or 0
                )

            except ValueError:

                flash(
                    "Days allotted must be a valid number.",
                    "danger",
                )

                return redirect(
                    url_for(
                        "settings.edit_squad",
                        squad_id=squad.id,
                    )
                )

            if squad_days < 0:

                flash(
                    "Days allotted cannot be negative.",
                    "danger",
                )

                return redirect(
                    url_for(
                        "settings.edit_squad",
                        squad_id=squad.id,
                    )
                )

            # --------------------------------------------------
            # Update Squad
            # --------------------------------------------------

            squad.squad_no = new_squad_no

            squad.panchayath_id = (
                panchayath.id
            )

            squad.squad_days = squad_days

            # --------------------------------------------------
            # Update Existing Members
            # --------------------------------------------------

            for member in squad.members:

                prefix = (
                    f"member_{member.id}_"
                )

                member_name = (
                    request.form.get(
                        prefix + "name",
                        ""
                    )
                    .strip()
                )

                designation = (
                    request.form.get(
                        prefix + "designation",
                        ""
                    )
                    .strip()
                )

                office = (
                    request.form.get(
                        prefix + "office",
                        ""
                    )
                    .strip()
                )

                pashudhan_id = (
                    request.form.get(
                        prefix + "pashudhan_id",
                        ""
                    )
                    .strip()
                )

                # ----------------------------------------------
                # Member Name Validation
                # ----------------------------------------------

                if not member_name:

                    flash(
                        (
                            "Squad member name cannot "
                            "be left blank."
                        ),
                        "danger",
                    )

                    db.session.rollback()

                    return redirect(
                        url_for(
                            "settings.edit_squad",
                            squad_id=squad.id,
                        )
                    )

                # ----------------------------------------------
                # Update Member
                # ----------------------------------------------

                member.member_name = (
                    member_name
                )

                member.designation = (
                    designation or None
                )

                member.office = (
                    office or None
                )

                member.pashudhan_id = (
                    pashudhan_id or None
                )

            # --------------------------------------------------
            # Commit
            # --------------------------------------------------

            db.session.commit()

            flash(
                (
                    f"Squad {squad.squad_no} and member "
                    "details updated successfully."
                ),
                "success",
            )

            return redirect(
                url_for(
                    "settings.edit_squad",
                    squad_id=squad.id,
                )
            )

        except Exception as ex:

            db.session.rollback()

            flash(
                (
                    "Unable to update squad details: "
                    f"{ex}"
                ),
                "danger",
            )

    # ------------------------------------------------------
    # Render Editor
    # ------------------------------------------------------

    return render_template(
        "settings/edit_squad.html",
        campaign=campaign,
        squad=squad,
        panchayaths=panchayaths,
        page_label="NCMS Administration",
        page_title="Edit Squad & Members",
        page_subtitle=(
            "Correct squad allocation and "
            "member master data"
        ),
    )