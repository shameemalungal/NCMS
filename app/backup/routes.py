from io import BytesIO

import pandas as pd

from flask import send_file, session

from app.backup import backup_bp
from app.auth.decorators import admin_required
from app.extensions import db
from app.models import (
    AuditLog,
    BackupHistory,
    Campaign,
    ImportHistory,
    Panchayath,
    Squad,
    SquadMember,
    Submission,
)
from app.utils.audit import log_audit


@backup_bp.route("/download")
@admin_required
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
                "Description": c.description,
                "Start Date": c.start_date,
                "End Date": c.end_date,
                "Status": c.status,
                "Active": c.is_active,
                "Submissions Open": c.submissions_open,
            }
            for c in Campaign.query.order_by(Campaign.id).all()
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
            for p in Panchayath.query.order_by(Panchayath.id).all()
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
                "Days Allotted": s.squad_days,
                "Target": s.target,
                "Status": s.status,
            }
            for s in Squad.query.order_by(Squad.id).all()
        ]).to_excel(
            writer,
            sheet_name="Squads",
            index=False
        )

        pd.DataFrame([
            {
                "ID": m.id,
                "Squad": m.squad_id,
                "Name": m.member_name,
                "Designation": m.designation,
                "Office": m.office,
                "Pashudhan ID": m.pashudhan_id,
                "Full Text": m.full_text,
            }
            for m in SquadMember.query.order_by(SquadMember.id).all()
        ]).to_excel(
            writer,
            sheet_name="Squad Members",
            index=False
        )

        pd.DataFrame([
            {
                "ID": x.id,
                "Squad": x.squad_id,
                "Days Worked": x.days_worked,
                "Vaccinations": x.vaccinations_done,
                "Pashudhan": x.pashudhan_entries,
                "Diseased": x.diseased,
                "Below 4 Months": x.below_4_months,
                "Pregnant": x.pregnant,
                "Unwilling": x.unwilling,
                "Other Count": x.other_count,
                "Other Reason": x.other_reason,
                "Remarks": x.remarks,
                "Vaccination %": x.vaccination_percentage,
                "Pashudhan %": x.pashudhan_percentage,
                "Vaccination Reason": x.vaccination_reason,
                "Pashudhan Reason": x.pashudhan_reason,
                "Source": x.source,
                "Status": x.status,
                "Submission Token": x.submission_token,
                "Submitted At": x.submitted_at,
            }
            for x in Submission.query.order_by(Submission.id).all()
        ]).to_excel(
            writer,
            sheet_name="Submissions",
            index=False
        )

        pd.DataFrame([
            {
                "ID": x.id,
                "Campaign": x.campaign_id,
                "Import Type": x.import_type,
                "Filename": x.filename,
                "Total Rows": x.total_rows,
                "Imported Rows": x.imported_rows,
                "Failed Rows": x.failed_rows,
                "Status": x.status,
                "Duration Seconds": x.duration_seconds,
                "Created At": x.created_at,
            }
            for x in ImportHistory.query.order_by(ImportHistory.id).all()
        ]).to_excel(
            writer,
            sheet_name="Import History",
            index=False
        )

        pd.DataFrame([
            {
                "ID": x.id,
                "Username": x.username,
                "Module": x.module,
                "Action": x.action,
                "IP Address": x.ip_address,
                "Created At": x.created_at,
            }
            for x in AuditLog.query.order_by(AuditLog.id).all()
        ]).to_excel(
            writer,
            sheet_name="Audit Logs",
            index=False
        )

        pd.DataFrame([
            {
                "ID": x.id,
                "Filename": x.filename,
                "Created By": x.created_by,
                "Created At": x.created_at,
            }
            for x in BackupHistory.query.order_by(BackupHistory.id).all()
        ]).to_excel(
            writer,
            sheet_name="Backup History",
            index=False
        )

    output.seek(0)

    filename = "NCMS_Backup.xlsx"

    history = BackupHistory(
        filename=filename,
        created_by=session.get(
            "admin_username",
            "Admin",
        ),
    )

    try:
        db.session.add(history)
        db.session.commit()
    except Exception:
        db.session.rollback()

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
        download_name=filename,
        mimetype=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
