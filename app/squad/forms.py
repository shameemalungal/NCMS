from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    IntegerField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    NumberRange,
    Length,
)

from app.models import Campaign, Panchayath


class SquadForm(FlaskForm):

    campaign_id = SelectField(
        "Campaign",
        coerce=int,
        validators=[DataRequired()],
    )

    panchayath_id = SelectField(
        "Panchayath",
        coerce=int,
        validators=[DataRequired()],
    )

    squad_no = IntegerField(
        "Squad Number",
        validators=[
            DataRequired(),
            NumberRange(min=1),
        ],
    )

    squad_days = IntegerField(
        "Squad Days",
        validators=[
            NumberRange(min=0),
        ],
        default=0,
    )

    target = IntegerField(
        "Target",
        validators=[
            NumberRange(min=0),
        ],
        default=0,
    )

    squad_member = StringField(
        "Squad Member",
        validators=[
            DataRequired(),
            Length(max=200),
        ],
    )

    office = StringField(
        "Office",
        validators=[
            Length(max=200),
        ],
    )

    pashudhan_id = StringField(
        "Pashudhan ID",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    submit = SubmitField("Save Squad")

    def load_choices(self):

        self.campaign_id.choices = [
            (c.id, f"{c.code} - {c.name}")
            for c in Campaign.query.order_by(Campaign.name).all()
        ]

        self.panchayath_id.choices = [
            (p.id, p.name)
            for p in Panchayath.query.order_by(Panchayath.name).all()
        ]