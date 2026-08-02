from sqlalchemy import func

from app.extensions import db
from app.models import Campaign, Panchayath, Squad, Submission


class DashboardService:

    @staticmethod
    def get_summary():

        active_campaign = (
            Campaign.query.filter_by(is_active=True)
            .first()
        )

        squad_query = Squad.query

        submission_query = Submission.query

        if active_campaign:
            squad_query = squad_query.filter(
                Squad.campaign_id == active_campaign.id
            )

            submission_query = (
                submission_query
                .join(Squad)
                .filter(
                    Squad.campaign_id == active_campaign.id
                )
            )

        total_squads = squad_query.count()

        submitted = submission_query.count()

        pending = max(total_squads - submitted, 0)

        vaccinations = (
            db.session.query(
                func.coalesce(
                    func.sum(Submission.vaccinations_done),
                    0,
                )
            )
            .select_from(Submission)
            .join(Squad)
        )

        entries = (
            db.session.query(
                func.coalesce(
                    func.sum(Submission.pashudhan_entries),
                    0,
                )
            )
            .select_from(Submission)
            .join(Squad)
        )

        if active_campaign:
            vaccinations = vaccinations.filter(
                Squad.campaign_id == active_campaign.id
            )

            entries = entries.filter(
                Squad.campaign_id == active_campaign.id
            )

        vaccinations = vaccinations.scalar() or 0

        entries = entries.scalar() or 0

        target = (
            squad_query.with_entities(
                func.coalesce(func.sum(Squad.target), 0)
            ).scalar()
            or 0
        )

        vaccination_percentage = 0

        if target:
            vaccination_percentage = round(
                (vaccinations / target) * 100,
                2,
            )

        pashudhan_percentage = 0

        if vaccinations:
            pashudhan_percentage = round(
                (entries / vaccinations) * 100,
                2,
            )

        recent_submissions = (
            submission_query
            .order_by(Submission.submitted_at.desc())
            .limit(10)
            .all()
        )

        pending_squads = (
            squad_query
            .filter(Squad.status == "Pending")
            .order_by(Squad.squad_no)
            .limit(10)
            .all()
        )

        panchayath_summary = (
            db.session.query(
                Panchayath.name,
                func.count(Squad.id).label("squads"),
                func.count(Submission.id).label("submitted"),
            )
            .join(Squad, Squad.panchayath_id == Panchayath.id)
            .outerjoin(
                Submission,
                Submission.squad_id == Squad.id,
            )
        )

        if active_campaign:
            panchayath_summary = panchayath_summary.filter(
                Panchayath.campaign_id == active_campaign.id
            )

        panchayath_summary = (
            panchayath_summary
            .group_by(Panchayath.id)
            .all()
        )

        return {

            "active_campaign": active_campaign,

            "submitted_squads": submitted,

            "pending_squads": pending,

            "total_squads": total_squads,

            "total_vaccinations": vaccinations,

            "total_entries": entries,

            "target_population": target,

            "vaccination_percentage": vaccination_percentage,

            "pashudhan_percentage": pashudhan_percentage,

            "recent_submissions": recent_submissions,

            "pending_squads_list": pending_squads,

            "panchayath_summary": panchayath_summary,

        }