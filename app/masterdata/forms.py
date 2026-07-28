from flask_wtf import FlaskForm

from wtforms import (
    SelectField,
    FileField,
    SubmitField,
)

from wtforms.validators import (
    DataRequired,
)

from flask_wtf.file import (
    FileAllowed,
    FileRequired,
)


class MasterDataImportForm(FlaskForm):

    campaign = SelectField(
        "Campaign",
        coerce=int,
        validators=[DataRequired()],
    )

    excel_file = FileField(
        "Excel File",
        validators=[
            FileRequired(message="Please select an Excel file."),
            FileAllowed(
                ["xlsx"],
                "Only .xlsx files are allowed."
            ),
        ],
    )

    validate = SubmitField("Validate File")

    import_data = SubmitField("Import Master Data")