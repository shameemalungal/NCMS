import os
from pathlib import Path
import tempfile

from flask import Blueprint, flash, render_template

from app.models import Campaign
from app.masterdata.forms import MasterDataImportForm
from app.masterdata.importer import MasterDataImporter
from app.masterdata.services import validate_excel
from app.auth.decorators import admin_required


masterdata_bp = Blueprint("masterdata", __name__, url_prefix="/masterdata")


@masterdata_bp.route("/", methods=["GET", "POST"])
@admin_required
def index():
    form = MasterDataImportForm()
    campaigns = Campaign.query.order_by(Campaign.name).all()
    form.campaign.choices = [(campaign.id, f"{campaign.name} ({campaign.code})") for campaign in campaigns]

    validation = None
    import_summary = None

    if form.validate_on_submit():
        uploaded = form.excel_file.data
        suffix = Path(uploaded.filename).suffix.lower() or ".xlsx"
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_path = temp_file.name
                uploaded.save(temp_path)

            validation = validate_excel(temp_path)
            if not validation.success:
                for error in validation.errors:
                    flash(error, "danger")
            elif form.import_data.data:
                import_summary = MasterDataImporter(
                    file_path=temp_path,
                    campaign_id=form.campaign.data,
                ).import_data()
                if import_summary["errors"]:
                    for error in import_summary["errors"]:
                        flash(error, "danger")
                else:
                    flash("Master data imported successfully.", "success")
            else:
                flash(validation.message, "info")
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    return render_template(
        "masterdata/index.html",
        page_title="Master Data Import",
        form=form,
        campaigns_available=bool(campaigns),
        validation=validation,
        import_summary=import_summary,
    )
