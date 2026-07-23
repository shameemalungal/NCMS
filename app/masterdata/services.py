from app.extensions import db
from app.models import Campaign, Panchayath, Squad


class MasterDataService:

    @staticmethod
    def get_or_create_campaign(name):

        campaign = Campaign.query.filter_by(name=name).first()

        if campaign:
            return campaign, False

        campaign = Campaign(
            name=name,
            status="Active"
        )

        db.session.add(campaign)

        return campaign, True

    @staticmethod
    def get_or_create_panchayath(name, population):

        p = Panchayath.query.filter_by(name=name).first()

        if p:
            p.population = population
            return p, False

        p = Panchayath(
            name=name,
            population=population
        )

        db.session.add(p)

        return p, True

    @staticmethod
    def get_or_create_squad(
        campaign,
        panchayath,
        squad_no,
        squad_days,
        squad_member,
        office,
        pashudhan_id,
        submission_token
    ):

        squad = Squad.query.filter_by(
            campaign_id=campaign.id,
            pashudhan_id=pashudhan_id
        ).first()

        if squad:

            squad.squad_no = squad_no
            squad.squad_days = squad_days
            squad.squad_member = squad_member
            squad.office = office

            return squad, False

        squad = Squad(
            campaign=campaign,
            panchayath=panchayath,
            squad_no=squad_no,
            squad_days=squad_days,
            squad_member=squad_member,
            office=office,
            pashudhan_id=pashudhan_id,
            submission_token=submission_token,
            status="Pending"
        )

        db.session.add(squad)

        return squad, True