from io import BytesIO

import pandas as pd

from flask import send_file

from app.backup import backup_bp
from app.models import (
    Campaign,
    Panchayath,
    Squad,
    Submission,
)
from flask import session
from app.utils.audit import log_audit


@backup_bp.route("/download")
def download_backup():

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        pd.DataFrame([
            {
                "ID": c.id,
                "Name": c.name,
                "Code": c.code,
                "Status": c.status,
            }
            for c in Campaign.query.all()
        ]).to_excel(
            writer,
            sheet_name="Campaigns",
            index=False
        )

        pd.DataFrame([
            {
                "ID": p.id,
                "Campaign": p.campaign_id,
                "Name": p.name,
                "Population": p.population,
            }
            for p in Panchayath.query.all()
        ]).to_excel(
            writer,
            sheet_name="Panchayaths",
            index=False
        )

        pd.DataFrame([
            {
                "ID": s.id,
                "Campaign": s.campaign_id,
                "Panchayath": s.panchayath_id,
                "Squad": s.squad_no,
                "Target": s.target,
            }
            for s in Squad.query.all()
        ]).to_excel(
            writer,
            sheet_name="Squads",
            index=False
        )

        pd.DataFrame([
            {
                "ID": x.id,
                "Squad": x.squad_id,
                "Vaccinations": x.vaccinations_done,
                "Pashudhan": x.pashudhan_entries,
            }
            for x in Submission.query.all()
        ]).to_excel(
            writer,
            sheet_name="Submissions",
            index=False
        )

    output.seek(0)

    log_audit(
        username=session.get(
            "admin_username",
            "Admin"
        ),
        module="Backup",
        action="Downloaded NCMS backup"
    )

    return send_file(
        output,
        as_attachment=True,
        download_name="NCMS_Backup.xlsx",
        mimetype=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )