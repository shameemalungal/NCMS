from datetime import datetime

from app.extensions import db


# ==========================================================
# Campaign
# ==========================================================

class Campaign(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    start_date = db.Column(db.Date)

    end_date = db.Column(db.Date)

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Active"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    squads = db.relationship(
        "Squad",
        backref="campaign",
        lazy=True,
        cascade="all, delete"
    )


# ==========================================================
# Panchayath
# ==========================================================

class Panchayath(db.Model):
    __tablename__ = "panchayaths"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    population = db.Column(
        db.Integer,
        default=0
    )

    squads = db.relationship(
        "Squad",
        backref="panchayath",
        lazy=True
    )


# ==========================================================
# Squad
# ==========================================================

class Squad(db.Model):
    __tablename__ = "squads"

    id = db.Column(db.Integer, primary_key=True)

    campaign_id = db.Column(
        db.Integer,
        db.ForeignKey("campaigns.id"),
        nullable=False
    )

    panchayath_id = db.Column(
        db.Integer,
        db.ForeignKey("panchayaths.id"),
        nullable=False
    )

    squad_no = db.Column(
        db.Integer,
        nullable=False
    )

    squad_days = db.Column(
        db.Integer,
        default=0
    )

    squad_member = db.Column(
        db.String(200),
        nullable=False
    )

    office = db.Column(
        db.String(200)
    )

    pashudhan_id = db.Column(
        db.String(100),
        nullable=False
    )

    submission_token = db.Column(
        db.String(100),
        unique=True
    )

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    submission = db.relationship(
        "Submission",
        backref="squad",
        uselist=False,
        cascade="all, delete-orphan"
    )


# ==========================================================
# Submission
# ==========================================================

class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)

    squad_id = db.Column(
        db.Integer,
        db.ForeignKey("squads.id"),
        unique=True,
        nullable=False
    )

    days_worked = db.Column(
        db.Integer,
        default=0
    )

    vaccinations_done = db.Column(
        db.Integer,
        default=0
    )

    pashudhan_entries = db.Column(
        db.Integer,
        default=0
    )

    diseased = db.Column(
        db.Integer,
        default=0
    )

    below_4_months = db.Column(
        db.Integer,
        default=0
    )

    pregnant = db.Column(
        db.Integer,
        default=0
    )

    unwilling = db.Column(
        db.Integer,
        default=0
    )

    other_reason = db.Column(
        db.String(250)
    )

    other_count = db.Column(
        db.Integer,
        default=0
    )

    vaccination_percentage = db.Column(
        db.Float,
        default=0
    )

    pashudhan_percentage = db.Column(
        db.Float,
        default=0
    )

    vaccination_reason = db.Column(
        db.Text
    )

    pashudhan_reason = db.Column(
        db.Text
    )

    submitted_from = db.Column(
        db.String(50)
    )

    status = db.Column(
        db.String(20),
        default="Submitted"
    )

    submitted_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )