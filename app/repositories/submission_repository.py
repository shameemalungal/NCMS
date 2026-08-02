from app.extensions import db
from app.models import Submission


class SubmissionRepository:

    @staticmethod
    def get_by_squad_id(squad_id):
        return Submission.query.filter_by(
            squad_id=squad_id
        ).first()

    @staticmethod
    def squad_already_submitted(squad_id):
        return (
            Submission.query.filter_by(
                squad_id=squad_id
            ).first()
            is not None
        )

    @staticmethod
    def get_by_token(token):
        return Submission.query.filter_by(
            submission_token=token
        ).first()

    @staticmethod
    def add(submission):
        db.session.add(submission)

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()