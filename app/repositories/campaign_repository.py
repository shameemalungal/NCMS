from sqlalchemy import func

from app.extensions import db
from app.models import Submission, Squad


class DashboardRepository:

    @staticmethod
    def squad_count():

        return db.session.query(

            func.count(Squad.id)

        ).scalar() or 0

    @staticmethod
    def submission_count():

        return db.session.query(

            func.count(Submission.id)

        ).scalar() or 0