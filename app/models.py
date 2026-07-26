from datetime import datetime

from app.extensions import db


# ==========================================================
# Campaign
# ==========================================================

class Campaign(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    code = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True
    )

    description = db.Column(
        db.Text
    )

    start_date = db.Column(
        db.Date
    )

    end_date = db.Column(
        db.Date
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Draft",
        index=True
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    squads = db.relationship(
        "Squad",
        back_populates="campaign",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Campaign {self.code}>"

    @property
    def total_squads(self):
        return len(self.squads)

    @property
    def total_submissions(self):
        return sum(
            1 for squad in self.squads
            if squad.submission is not None
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
        nullable=False,
        index=True
    )

    population = db.Column(
        db.Integer,
        default=0
    )

    squads = db.relationship(
        "Squad",
        back_populates="panchayath",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Panchayath {self.name}>"


# ==========================================================
# Squad
# ==========================================================

class Squad(db.Model):
    __tablename__ = "squads"

    __table_args__ = (
        db.UniqueConstraint(
            "campaign_id",
            "squad_no",
            name="uq_campaign_squad"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    campaign_id = db.Column(
        db.Integer,
        db.ForeignKey("campaigns.id"),
        nullable=False,
        index=True
    )

    panchayath_id = db.Column(
        db.Integer,
        db.ForeignKey("panchayaths.id"),
        nullable=False,
        index=True
    )

    squad_no = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    squad_days = db.Column(
        db.Integer,
        default=0
    )

    target = db.Column(
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
        unique=True,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Pending",
        index=True
    )

    campaign = db.relationship(
        "Campaign",
        back_populates="squads"
    )

    panchayath = db.relationship(
        "Panchayath",
        back_populates="squads"
    )

    submission = db.relationship(
        "Submission",
        back_populates="squad",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Squad {self.squad_no}>"


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
        default="Submitted",
        index=True
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

    squad = db.relationship(
        "Squad",
        back_populates="submission"
    )

    def __repr__(self):
        return f"<Submission {self.id}>"