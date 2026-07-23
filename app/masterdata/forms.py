from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class MasterDataUploadForm(FlaskForm):
    campaign_name = StringField(
        "Campaign Name",
        validators=[DataRequired()],
        default="NADCP Phase 8"
    )

    excel_file = FileField(
        "Excel File",
        validators=[FileRequired()]
    )

    submit = SubmitField("Import Master Data")