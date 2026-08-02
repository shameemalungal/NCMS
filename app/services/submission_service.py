from datetime import datetime
import secrets

from app.constants import (
    SquadStatus,
    SubmissionStatus,
)
from app.models import Submission
from app.repositories.submission_repository import (
    SubmissionRepository,
)


class DuplicateSubmissionError(Exception):
    """Raised when a squad already has a submission."""
    pass


class SubmissionService:

    @staticmethod
    def generate_token(campaign_code):

        prefix = (
            campaign_code
            .upper()
            .replace(" ", "")
            .replace("-", "")
        )

        while True:

            random_part = secrets.token_hex(4)[:7].upper()

            token = f"{prefix}-{random_part}"

            if SubmissionRepository.get_by_token(token) is None:
                return token

    @staticmethod
    def squad_already_submitted(squad_id):

        return SubmissionRepository.squad_already_submitted(
            squad_id
        )

    @staticmethod
    def create_submission(
        squad,
        form,
        source="Web",
    ):

        # --------------------------------------------------
        # Duplicate protection
        # --------------------------------------------------

        if SubmissionService.squad_already_submitted(
            squad.id
        ):
            raise DuplicateSubmissionError(
                "This squad has already submitted its report."
            )

        # --------------------------------------------------
        # Reference number
        # --------------------------------------------------

        token = SubmissionService.generate_token(
            squad.campaign.code
        )

        # --------------------------------------------------
        # Create submission
        # --------------------------------------------------

        submission = Submission(
            squad_id=squad.id,

            days_worked=form.days_worked.data or 0,

            vaccinations_done=(
                form.vaccinations_done.data or 0
            ),

            pashudhan_entries=(
                form.pashudhan_entries.data or 0
            ),

            diseased=form.diseased.data or 0,

            below_4_months=(
                form.below_4_months.data or 0
            ),

            pregnant=form.pregnant.data or 0,

            unwilling=form.unwilling.data or 0,

            other_reason=(
                form.other_reason.data or ""
            ).strip(),

            other_count=form.other_count.data or 0,

            remarks=(
                form.remarks.data or ""
            ).strip(),

            source=source,

            status=SubmissionStatus.SUBMITTED,

            submission_token=token,

            submitted_at=datetime.utcnow(),
        )

        # --------------------------------------------------
        # Percentages
        # --------------------------------------------------

        target = squad.target or 0

        if target > 0:

            submission.vaccination_percentage = round(
                (
                    submission.vaccinations_done
                    / target
                ) * 100,
                2,
            )

            submission.pashudhan_percentage = round(
                (
                    submission.pashudhan_entries
                    / target
                ) * 100,
                2,
            )

        # --------------------------------------------------
        # Optional reason fields
        # --------------------------------------------------

        if hasattr(form, "vaccination_reason"):

            submission.vaccination_reason = (
                form.vaccination_reason.data
                or None
            )

        if hasattr(form, "pashudhan_reason"):

            submission.pashudhan_reason = (
                form.pashudhan_reason.data
                or None
            )

        # --------------------------------------------------
        # ONE TRANSACTION
        # --------------------------------------------------

        try:

            SubmissionRepository.add(submission)

            squad.status = SquadStatus.SUBMITTED

            SubmissionRepository.commit()

        except Exception:

            SubmissionRepository.rollback()

            raise

        return submission