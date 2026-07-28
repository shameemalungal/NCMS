from pathlib import Path
import tempfile

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
)

from app.models import Campaign
from app.masterdata.forms import MasterDataImportForm
from app.masterdata.services import validate_excel


masterdata_bp = Blueprint(
    "masterdata",
    __name__,
    url_prefix="/masterdata",
)


@masterdata_bp.route("/", methods=["GET", "POST"])
def index():

    form = MasterDataImportForm()

    campaigns = Campaign.query.order_by(
        Campaign.name
    ).all()

    form.campaign.choices = [
        (c.id, f"{c.name} ({c.code})")
        for c in campaigns
    ]

    validation = None

    if request.method == "POST":

        if form.validate_on_submit():

            uploaded = form.excel_file.data

            suffix = Path(uploaded.filename).suffix

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as temp:

                uploaded.save(temp.name)

                validation = validate_excel(temp.name)

            if validation.success:

                flash(
                    validation.message,
                    "success"
                )

            else:

                for error in validation.errors:

                    flash(
                        error,
                        "danger"
                    )

    return render_template(
        "masterdata/index.html",
        page_title="Master Data Import",
        form=form,
        validation=validation,
    )