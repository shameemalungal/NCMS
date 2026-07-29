from pathlib import Path
import tempfile

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models import Campaign
from app.masterdata.forms import MasterDataImportForm
from app.masterdata.importer import MasterDataImporter
from app.masterdata.services import validate_excel


masterdata_bp = Blueprint("masterdata", __name__, url_prefix="/masterdata")


@masterdata_bp.route("/", methods=["GET", "POST"])
def index():
    form = MasterDataImportForm()

    campaigns = Campaign.query.order_by(Campaign.name).all()
    form.campaign.choices = [(c.id, f"{c.name} ({c.code})") for c in campaigns]

    validation = None
    import_summary = None
    preview_mode = False

    if form.validate_on_submit():
        uploaded = form.excel_file.data
        suffix = Path(uploaded.filename).suffix or ".xlsx"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            uploaded.save(temp.name)
            validation = validate_excel(temp.name)

            if not validation.success:
                for error in validation.errors:
                    flash(error, "danger")
                return render_template(
                    "masterdata/index.html",
                    page_title="Master Data Import",
                    form=form,
                    validation=validation,
                    import_summary=None,
                    preview_mode=False,
                )

            preview_mode = True

            if form.import_data.data:
                importer = MasterDataImporter(
                    file_path=temp.name,
                    campaign_id=form.campaign.data,
                )
                import_summary = importer.import_data()
                if import_summary.get("errors"):
                    for error in import_summary["errors"]:
                        flash(error, "danger")
                else:
                    flash("Master data imported successfully.", "success")
                    return redirect(url_for("masterdata.index"))
            else:
                flash(validation.message, "info")

    return render_template(
        "masterdata/index.html",
        page_title="Master Data Import",
        form=form,
        validation=validation,
        import_summary=import_summary,
        preview_mode=preview_mode,
    )
