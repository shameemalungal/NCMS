from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import FileField, SelectField, SubmitField
from wtforms.validators import DataRequired


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
            FileAllowed(["xlsx"], "Only .xlsx files are allowed."),
        ],
    )

    validate_file = SubmitField("Validate File")
    import_data = SubmitField("Import Master Data")
