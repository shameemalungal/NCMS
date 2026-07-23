import os
import tempfile

from flask import (
    flash,
    redirect,
    render_template,
    url_for
)

from app.masterdata import masterdata_bp
from app.masterdata.forms import MasterDataUploadForm
from app.masterdata.importer import MasterDataImporter


@masterdata_bp.route("/", methods=["GET", "POST"])
def index():

    form = MasterDataUploadForm()

    if form.validate_on_submit():

        campaign_name = form.campaign_name.data.strip()
        uploaded_file = form.excel_file.data

        # Create a Windows-safe temporary file
        fd, temp_path = tempfile.mkstemp(suffix=".xlsx")
        os.close(fd)

        try:
            # Save uploaded file
            uploaded_file.save(temp_path)

            # Run importer
            importer = MasterDataImporter(
                temp_path,
                campaign_name
            )

            summary = importer.import_data()

            # Print summary in terminal (for debugging)
            print("\n========== IMPORT SUMMARY ==========")
            print(summary)
            print("====================================\n")

            if summary["errors"]:

                for error in summary["errors"]:
                    flash(error, "danger")

            else:

                flash(
                    (
                        f"Import completed successfully.<br><br>"
                        f"<strong>Campaign:</strong> {campaign_name}<br>"
                        f"<strong>Panchayaths Created:</strong> {summary['panchayaths_created']}<br>"
                        f"<strong>Panchayaths Updated:</strong> {summary['panchayaths_updated']}<br>"
                        f"<strong>Squads Created:</strong> {summary['squads_created']}<br>"
                        f"<strong>Squads Updated:</strong> {summary['squads_updated']}"
                    ),
                    "success"
                )

        except Exception as e:

            print("\n========== IMPORT ERROR ==========")
            print(e)
            print("==================================\n")

            flash(f"Unexpected Error: {str(e)}", "danger")

        finally:

            # Delete temporary file
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except PermissionError:
                    pass

        return redirect(url_for("masterdata.index"))

    return render_template(
        "masterdata/index.html",
        form=form
    )