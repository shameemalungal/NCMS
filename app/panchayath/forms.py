from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    ValidationError,
)

from app.models import Panchayath


class PanchayathForm(FlaskForm):

    name = StringField(
        "Panchayath Name",
        validators=[
            DataRequired(),
            Length(max=120),
        ],
    )

    submit = SubmitField("Save")

    def __init__(self, original_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, field):

        name = field.data.strip().title()

        if self.original_name:

            if name.lower() == self.original_name.lower():
                field.data = name
                return

        existing = Panchayath.query.filter_by(name=name).first()

        if existing:
            raise ValidationError(
                "Panchayath already exists."
            )

        field.data = name