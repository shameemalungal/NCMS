from app.models import Panchayath, Squad, Submission


class MonitoringRepository:

    @staticmethod
    def get_panchayaths(campaign_id):

        return Panchayath.query.filter_by(
            campaign_id=campaign_id
        ).all()

    @staticmethod
    def get_squads(panchayath_id):

        return Squad.query.filter_by(
            panchayath_id=panchayath_id
        ).all()

    @staticmethod
    def get_submission(squad_id):

        return Submission.query.filter_by(
            squad_id=squad_id
        ).first()