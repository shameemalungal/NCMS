from sqlalchemy import func

from app.extensions import db
from app.models import Squad, Submission


class DashboardService:

    @staticmethod
    def summary():

        submitted = (
            db.session.query(func.count(Submission.id))
            .scalar()
            or 0
        )

        squads = (
            db.session.query(func.count(Squad.id))
            .scalar()
            or 0
        )

        pending = max(squads - submitted, 0)

        vaccinations = (
            db.session.query(
                func.coalesce(func.sum(Submission.vaccinations_done), 0)
            ).scalar()
        )

        entries = (
            db.session.query(
                func.coalesce(func.sum(Submission.pashudhan_entries), 0)
            ).scalar()
        )

        percentage = 0

        if squads:

            percentage = round((submitted / squads) * 100, 1)

        return {

            "submitted_squads": submitted,

            "pending_squads": pending,

            "total_vaccinations": vaccinations,

            "total_entries": entries,

            "vaccination_percentage": percentage

        }

    @staticmethod
    def recent(limit=10):

        return (

            Submission.query

            .order_by(Submission.created_at.desc())

            .limit(limit)

            .all()

        )