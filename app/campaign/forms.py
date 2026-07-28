from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    DateField,
    SelectField,
    BooleanField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length


class CampaignForm(FlaskForm):

    name = StringField(
        "Campaign Name",
        validators=[DataRequired(), Length(max=100)],
        render_kw={"placeholder": "Example: NADCP Phase IX"},
    )

    code = StringField(
        "Campaign Code",
        validators=[DataRequired(), Length(max=30)],
        render_kw={"placeholder": "Example: NADCP-IX"},
    )

    description = TextAreaField(
        "Description",
        validators=[Length(max=1000)],
        render_kw={"rows": 4},
    )

    start_date = DateField(
        "Start Date",
        format="%Y-%m-%d",
    )

    end_date = DateField(
        "End Date",
        format="%Y-%m-%d",
    )

    status = SelectField(
        "Status",
        choices=[
            ("Draft", "Draft"),
            ("Active", "Active"),
            ("Completed", "Completed"),
            ("Closed", "Closed"),
        ],
    )

    is_active = BooleanField("Active Campaign")

    submit = SubmitField("Save Campaign")