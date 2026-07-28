from flask import Blueprint, render_template, request, flash, redirect
from werkzeug.utils import secure_filename
import os

from app.services.masterdata_service import MasterDataImporter

bp = Blueprint("import", __name__)


@bp.route("/import", methods=["GET", "POST"])
def import_master():

    if request.method == "POST":

        file = request.files["file"]

        filename = secure_filename(file.filename)

        path = os.path.join("uploads", filename)

        file.save(path)

        importer = MasterDataImporter(path)

        importer.import_data()

        flash("Import completed successfully")

        return redirect("/")

    return render_template("import.html")