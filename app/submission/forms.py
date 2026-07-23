from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import NumberRange, Optional
from wtforms.widgets import NumberInput


NUMBER_WIDGET = NumberInput()


class SubmissionForm(FlaskForm):

    days_worked = IntegerField(
        "A. Squad Days Worked",
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=40,
                message="Days worked must be between 0 and 40."
            )
        ],
        widget=NUMBER_WIDGET,
        render_kw={
            "placeholder": "0",
            "autocomplete": "off",
            "step": "1",
            "min": "0",
            "max": "40",
            "autofocus": True
        }
    )

    vaccinations_done = IntegerField(
        "B. Vaccinations Done",
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Value cannot be negative."
            )
        ],
        widget=NUMBER_WIDGET,
        render_kw={
            "placeholder": "0",
            "autocomplete": "off",
            "step": "1",
            "min": "0"
        }
    )

    pashudhan_entries = IntegerField(
        "C. Pashudhan Entries",
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Value cannot be negative."
            )
        ],
        widget=NUMBER_WIDGET,
        render_kw={
            "placeholder": "0",
            "autocomplete": "off",
            "step": "1",
            "min": "0"
        }
    )

    diseased = IntegerField(
        "D. Diseased",
        default=None,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Value cannot be negative."
            )
        ],
        widget=NUMBER_WIDGET,
        render_kw={
            "placeholder": "0",
            "autocomplete": "off",
            "step": "1",
            "min": "0"
        }
    )

    below_4_months = IntegerField(
        "E. Below 4 Months",
        default=None,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Value cannot be negative."
            )
        ],
        widget=NUMBER_WIDGET,
        render_kw={
            "placeholder": "0",
            "autocomplete": "off",
            "step": "1",
            "min": "0"
        }
    )

    pregnant = IntegerField(
        "F. Pregnant",
        default=None,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Value cannot be negative."
            )
        ],
        widget=NUMBER_WIDGET,
        render_kw={
            "placeholder": "0",
            "autocomplete": "off",
            "step": "1",
            "min": "0"
        }
    )

    unwilling = IntegerField(
        "G. Unwilling",
        default=None,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Value cannot be negative."
            )
        ],
        widget=NUMBER_WIDGET,
        render_kw={
            "placeholder": "0",
            "autocomplete": "off",
            "step": "1",
            "min": "0"
        }
    )

    submit = SubmitField(
        "💾 Save Submission"
    )