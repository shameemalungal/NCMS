from flask import flash, render_template, request

from app.extensions import db
from app.models import Squad, Submission
from app.submission import submission_bp
from app.submission.forms import SubmissionForm


@submission_bp.route("/<token>", methods=["GET", "POST"])
def submit(token):

    squad = Squad.query.filter_by(
        submission_token=token
    ).first()

    if squad is None:
        return "<h2>Invalid Submission Link</h2>", 404

    if squad.submission:
        flash(
            "This squad has already submitted the report.",
            "warning"
        )
        return render_template(
            "submission/success.html",
            squad=squad
        )

    form = SubmissionForm()

    if form.validate_on_submit():
        try:
            other_reasons = request.form.getlist("other_reason[]")
            other_counts = request.form.getlist("other_count[]")

            first_reason = ""
            first_count = 0

            if other_reasons:
                first_reason = other_reasons[0].strip()

            if other_counts:
                try:
                    first_count = int(other_counts[0] or 0)
                except ValueError:
                    first_count = 0

            submission = Submission(
                squad_id=squad.id,
                days_worked=form.days_worked.data or 0,
                vaccinations_done=form.vaccinations_done.data or 0,
                pashudhan_entries=form.pashudhan_entries.data or 0,
                diseased=form.diseased.data or 0,
                below_4_months=form.below_4_months.data or 0,
                pregnant=form.pregnant.data or 0,
                unwilling=form.unwilling.data or 0,
                other_reason=first_reason,
                other_count=first_count,
                vaccination_reason=(form.remarks.data or "").strip(),
                vaccination_percentage=0,
                pashudhan_percentage=0,
                submitted_from=request.remote_addr,
                status="Submitted"
            )

            db.session.add(submission)
            squad.status = "Submitted"
            db.session.commit()

            return render_template(
                "submission/success.html",
                squad=squad
            )

        except Exception as ex:
            db.session.rollback()
            flash(
                f"Error : {ex}",
                "danger"
            )

    return render_template(
        "submission/form.html",
        squad=squad,
        form=form,
        members=squad.members
    )
