from datetime import datetime

from flask import request

from app.extensions import db
from app.models import (
    Squad,
    Submission,
    SubmissionHistory,
    AuditLog,
)
from app.constants import SquadStatus


class ResubmissionService:
    """
    Handles administrator-authorised squad re-submission.

    Workflow:

        Live Submission
              |
              v
        Archive complete submission
              |
              v
        Record admin audit action
              |
              v
        Delete live Submission
              |
              v
        Reset Squad to PENDING
              |
              v
        Squad can submit again

    The Squad, Panchayath and Squad Member records
    are never deleted.
    """

    @staticmethod
    def allow_resubmission(
        squad_id,
        username,
    ):
        """
        Archive the current live submission and remove it
        from live data so the squad can submit again.

        The archive, audit entry, deletion and squad reset
        are performed in one database transaction.
        """

        # --------------------------------------------------
        # Find squad
        # --------------------------------------------------

        squad = (
            Squad.query
            .filter_by(id=squad_id)
            .first()
        )

        if squad is None:
            return {
                "success": False,
                "message": "Squad not found.",
            }

        # --------------------------------------------------
        # Find current live submission
        # --------------------------------------------------

        submission = (
            Submission.query
            .filter_by(
                squad_id=squad.id
            )
            .first()
        )

        if submission is None:
            return {
                "success": False,
                "message": (
                    "This squad does not currently "
                    "have a live submission."
                ),
            }

        # --------------------------------------------------
        # Preserve identifying information
        # --------------------------------------------------

        submission_id = submission.id
        squad_number = squad.squad_no

        # --------------------------------------------------
        # Administrator
        # --------------------------------------------------

        if not username:
            username = "Administrator"

        # --------------------------------------------------
        # Create complete historical snapshot
        # --------------------------------------------------

        history = SubmissionHistory(
            original_submission_id=(
                submission.id
            ),

            squad_id=(
                submission.squad_id
            ),

            days_worked=(
                submission.days_worked
            ),

            vaccinations_done=(
                submission.vaccinations_done
            ),

            pashudhan_entries=(
                submission.pashudhan_entries
            ),

            diseased=(
                submission.diseased
            ),

            below_4_months=(
                submission.below_4_months
            ),

            pregnant=(
                submission.pregnant
            ),

            unwilling=(
                submission.unwilling
            ),

            other_reason=(
                submission.other_reason
            ),

            other_count=(
                submission.other_count
            ),

            remarks=(
                submission.remarks
            ),

            vaccination_percentage=(
                submission.vaccination_percentage
            ),

            pashudhan_percentage=(
                submission.pashudhan_percentage
            ),

            vaccination_reason=(
                submission.vaccination_reason
            ),

            pashudhan_reason=(
                submission.pashudhan_reason
            ),

            source=(
                submission.source
            ),

            status=(
                submission.status
            ),

            submission_token=(
                submission.submission_token
            ),

            submitted_at=(
                submission.submitted_at
            ),

            archived_at=datetime.utcnow(),

            archived_by=username,
        )

        # --------------------------------------------------
        # Create audit log entry
        #
        # IMPORTANT:
        # Do NOT use log_audit() here because that utility
        # commits independently. We need everything in the
        # same transaction.
        # --------------------------------------------------

        audit = AuditLog(
            username=username,

            module="Monitoring",

            action=(
                "Allowed re-submission for "
                f"Squad {squad_number}. "
                f"Previous submission ID: "
                f"{submission_id}. "
                "Previous submission archived."
            ),

            ip_address=(
                request.remote_addr
                if request
                else None
            ),
        )

        # --------------------------------------------------
        # Transaction
        # --------------------------------------------------

        try:

            # ----------------------------------------------
            # 1. Archive old submission
            # ----------------------------------------------

            db.session.add(history)

            # ----------------------------------------------
            # 2. Record administrator action
            # ----------------------------------------------

            db.session.add(audit)

            # ----------------------------------------------
            # 3. Remove old live submission
            # ----------------------------------------------

            db.session.delete(
                submission
            )

            # ----------------------------------------------
            # 4. Reset squad
            # ----------------------------------------------

            squad.status = (
                SquadStatus.PENDING
            )

            squad.resubmission_allowed = True

            squad.resubmission_allowed_at = (
                datetime.utcnow()
            )

            squad.resubmission_allowed_by = (
                username
            )

            # ----------------------------------------------
            # 5. Commit everything atomically
            # ----------------------------------------------

            db.session.commit()

        except Exception:

            db.session.rollback()

            raise

        # --------------------------------------------------
        # Success
        # --------------------------------------------------

        return {
            "success": True,
            "message": (
                f"Re-submission allowed for "
                f"Squad {squad_number}. "
                "The previous submission has been "
                "archived and removed from live data."
            ),
        }
    # ==================================================
    # Submission History
    # ==================================================

    @staticmethod
    def get_submission_history():
        """
        Return archived submission history records,
        newest archived submission first.
        """

        return (
            db.session.query(
                SubmissionHistory,
                Squad,
            )
            .join(
                Squad,
                SubmissionHistory.squad_id
                == Squad.id,
            )
            .order_by(
                SubmissionHistory.archived_at.desc()
            )
            .all()
        )