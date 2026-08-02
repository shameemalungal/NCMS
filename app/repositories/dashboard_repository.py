from app.models import (
    Campaign,
    Squad,
    Submission,
)


class DashboardRepository:

    @staticmethod
    def get_active_campaign():

        return Campaign.query.filter_by(
            is_active=True
        ).first()


    @staticmethod
    def get_campaign_squads(campaign_id):

        return Squad.query.filter_by(
            campaign_id=campaign_id
        ).all()


    @staticmethod
    def get_campaign_submissions(campaign_id):

        return (
            Submission.query
            .join(
                Squad,
                Submission.squad_id == Squad.id
            )
            .filter(
                Squad.campaign_id == campaign_id
            )
            .all()
        )