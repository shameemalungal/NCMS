from datetime import datetime

from app.extensions import db
from app.constants import (
    CampaignStatus,
    SquadStatus,
    SubmissionStatus,
)

class TimestampMixin:

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# ==========================================================
# Campaign
# ==========================================================

class Campaign(TimestampMixin, db.Model):
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
    default=SquadStatus.PENDING,
    index=True
)

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    # ------------------------------------------------------
    # Public Submission Control
    # ------------------------------------------------------

    submissions_open = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default="1",
    )

    
    squads = db.relationship(
        "Squad",
        back_populates="campaign",
        cascade="all, delete-orphan",
        lazy=True,
    )

    panchayaths = db.relationship(
        "Panchayath",
        back_populates="campaign",
        cascade="all, delete-orphan",
        lazy=True,
    )

    imports = db.relationship(
        "ImportHistory",
        back_populates="campaign",
        cascade="all, delete-orphan",
        lazy=True,
    )

    @property
    def total_population(self):
        return sum(panchayath.population for panchayath in self.panchayaths)

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

class Panchayath(TimestampMixin, db.Model):
    __tablename__ = "panchayaths"

    __table_args__ = (
        db.UniqueConstraint(
            "campaign_id",
            "name",
            name="uq_campaign_panchayath",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    campaign_id = db.Column(
        db.Integer,
        db.ForeignKey("campaigns.id"),
        nullable=False,
        index=True
    )

    name = db.Column(
        db.String(120),
        nullable=False,
        index=True
    )

    population = db.Column(
        db.Integer,
        default=0
    )

    campaign = db.relationship(
        "Campaign",
        back_populates="panchayaths",
        lazy=True,
    )

    squads = db.relationship(
        "Squad",
        back_populates="panchayath",
        cascade="all, delete-orphan",
        lazy=True,
    )

    @property
    def total_squads(self):
        return len(self.squads)

    def __repr__(self):
        return f"<Panchayath {self.name}>"


# ==========================================================
# Squad
# ==========================================================

class Squad(TimestampMixin, db.Model):
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
        nullable=False,
        default=0,
    )


    status = db.Column(
        db.String(20),
        default=SquadStatus.PENDING,
        index=True
    )

    campaign = db.relationship(
        "Campaign",
        back_populates="squads",
        lazy=True,
    )

    panchayath = db.relationship(
        "Panchayath",
        back_populates="squads",
        lazy=True,
    )

    submission = db.relationship(
        "Submission",
        back_populates="squad",
        uselist=False,
        cascade="all, delete-orphan",
        lazy=True,
    )

    members = db.relationship(
        "SquadMember",
        back_populates="squad",
        cascade="all, delete-orphan",
        lazy=True,
    )

    @property
    def member_count(self):
        return len(self.members)

    def __repr__(self):
        return f"<Squad {self.squad_no}>"


# ==========================================================
# Submission
# ==========================================================

class Submission(TimestampMixin, db.Model):
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

    remarks = db.Column(
        db.Text
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

    source = db.Column(
        db.String(50)
    )

    status = db.Column(
        db.String(20),
        default=SubmissionStatus.SUBMITTED,
        index=True
    )
    submission_token = db.Column(
        db.String(30),
        unique=True,
        nullable=True,
        index=True,
    )

    submitted_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

     
    squad = db.relationship(
        "Squad",
        back_populates="submission",
        lazy=True,
    )

    def __repr__(self):
        return f"<Submission {self.id}>"


class SquadMember(TimestampMixin, db.Model):
    __tablename__ = "squad_members"

    id = db.Column(db.Integer, primary_key=True)

    squad_id = db.Column(
        db.Integer,
        db.ForeignKey("squads.id"),
        nullable=False,
        index=True
    )

    member_name = db.Column(
        db.String(200),
        nullable=False
    )

    designation = db.Column(
        db.String(150)
    )

    office = db.Column(
        db.String(200)
    )

    pashudhan_id = db.Column(
        db.String(100),
        index=True
    )

    full_text = db.Column(db.Text)

    squad = db.relationship(
        "Squad",
        back_populates="members",
        lazy=True,
    )

    def __repr__(self):
        return f"<SquadMember {self.member_name}>"


class ImportHistory(TimestampMixin, db.Model):
    __tablename__ = "import_history"

    id = db.Column(db.Integer, primary_key=True)

    campaign_id = db.Column(
        db.Integer,
        db.ForeignKey("campaigns.id"),
        nullable=False,
        index=True,
    )

    import_type = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    total_rows = db.Column(db.Integer, default=0)
    imported_rows = db.Column(db.Integer, default=0)
    failed_rows = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), nullable=False, default="Pending")
    duration_seconds = db.Column(db.Integer, default=0)

    campaign = db.relationship(
        "Campaign",
        back_populates="imports",
        lazy=True,
    )

    def __repr__(self):
        return f"<ImportHistory {self.filename}>"
    # ==========================================================
# Audit Log
# ==========================================================

class AuditLog(TimestampMixin, db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.String(100),
        nullable=False,
        index=True,
    )

    module = db.Column(
        db.String(100),
        nullable=False,
        index=True,
    )

    action = db.Column(
        db.String(255),
        nullable=False,
    )

    ip_address = db.Column(
        db.String(50),
    )

    def __repr__(self):
        return (
            f"<AuditLog "
            f"{self.username} "
            f"{self.module}>"
        )
class BackupHistory(
    TimestampMixin,
    db.Model
):
    __tablename__ = "backup_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    created_by = db.Column(
        db.String(100),
        nullable=False
    )

    def __repr__(self):
        return (
            f"<BackupHistory "
            f"{self.filename}>"
        )
    