from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    DateField,
    SelectField,
    SubmitField,
    BooleanField,
)
from wtforms.validators import DataRequired, Length, ValidationError

from app.models import Campaign


class CampaignForm(FlaskForm):

    name = StringField(
        "Campaign Name",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    code = StringField(
        "Campaign Code",
        validators=[
            DataRequired(),
            Length(max=30)
        ]
    )

    description = TextAreaField(
        "Description"
    )

    start_date = DateField(
        "Start Date",
        validators=[DataRequired()],
        format="%Y-%m-%d"
    )

    end_date = DateField(
        "End Date",
        validators=[DataRequired()],
        format="%Y-%m-%d"
    )

    status = SelectField(
        "Status",
        choices=[
            ("Draft", "Draft"),
            ("Active", "Active"),
            ("Closed", "Closed"),
        ],
        validators=[DataRequired()]
    )

    is_active = BooleanField(
        "Set as Active Campaign"
    )

    submit = SubmitField("Save Campaign")

    def __init__(self, original_code=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_code = original_code

    def validate_code(self, field):
        if field.data == self.original_code:
            return

        campaign = Campaign.query.filter_by(code=field.data).first()

        if campaign:
            raise ValidationError(
                "Campaign code already exists."
            )

    def validate_end_date(self, field):
        if self.start_date.data and field.data:
            if field.data < self.start_date.data:
                raise ValidationError(
                    "End Date cannot be earlier than Start Date."
                )