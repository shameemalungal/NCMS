from flask import (
    render_template,
    request,
    send_file,
)

from app.reports import reports_bp
from app.reports.services import ReportService
from app.services.monitoring_service import MonitoringService


# ==========================================================
# Reports Dashboard
# ==========================================================

@reports_bp.route("/")
def index():

    # Reuse the established monitoring calculations.
    # This keeps report figures consistent with Squad Monitor.

    data = MonitoringService.get_dashboard()

    campaign = data.get("campaign")
    monitoring = data.get("monitoring", [])
    summary = data.get("summary", {})

    return render_template(
        "reports/index.html",
        campaign=campaign,
        monitoring=monitoring,
        summary=summary,
        page_label="NCMS Reports",
        page_title="Reports",
        page_subtitle=(
            "Campaign reports, achievement analysis "
            "and submission status"
        ),
    )


# ==========================================================
# Panchayath Achievement Report
# ==========================================================

@reports_bp.route("/panchayath-achievement")
def panchayath_achievement():

    data = MonitoringService.get_dashboard()

    campaign = data.get("campaign")
    monitoring = data.get("monitoring", [])
    summary = data.get("summary", {})

    return render_template(
        "reports/panchayath_achievement.html",
        campaign=campaign,
        monitoring=monitoring,
        summary=summary,
        page_label="NCMS Reports",
        page_title="Panchayath Achievement",
        page_subtitle=(
            "Panchayath-wise vaccination and "
            "Pashudhan achievement"
        ),
    )
# ==========================================================
# Squad-wise Report
# ==========================================================

@reports_bp.route("/squad-wise")
def squad_wise():

    # Reuse the same validated monitoring dataset.
    # submitted_squads already contains squad performance,
    # members, reasons and submission information.

    data = MonitoringService.get_dashboard()

    campaign = data.get("campaign")
    monitoring = data.get("monitoring", [])
    summary = data.get("summary", {})

    return render_template(
        "reports/squad_wise.html",
        campaign=campaign,
        monitoring=monitoring,
        summary=summary,
        page_label="NCMS Reports",
        page_title="Squad-wise Report",
        page_subtitle=(
            "Detailed squad-wise campaign "
            "performance and submission analysis"
        ),
    )

# ==========================================================
# Pending Submission Report
# ==========================================================

@reports_bp.route("/pending-submissions")
def pending_submissions():

    # Reuse the validated monitoring dataset.
    # Pending squads already contain Panchayath,
    # squad and member information.

    data = MonitoringService.get_dashboard()

    campaign = data.get("campaign")
    monitoring = data.get("monitoring", [])
    summary = data.get("summary", {})

    return render_template(
        "reports/pending_submissions.html",
        campaign=campaign,
        monitoring=monitoring,
        summary=summary,
        page_label="NCMS Reports",
        page_title="Pending Submissions",
        page_subtitle=(
            "Squads that have not yet submitted "
            "campaign data"
        ),
    )

# ==========================================================
# Squad-wise Excel Export
# ==========================================================

@reports_bp.route("/squad-wise/export")
def export_squad_wise():

    # ------------------------------------------------------
    # Requested report category
    # ------------------------------------------------------

    report_filter = request.args.get(
        "filter",
        "all",
    ).strip().lower()


    # ------------------------------------------------------
    # Allow only known Squad-wise filters
    # ------------------------------------------------------

    allowed_filters = {
        "all",
        "submitted",
        "pending",
        "vaccination-achieved",
        "pashudhan-achieved",
        "both-achieved",
        "low-vaccination",
        "low-pashudhan",
        "low-both",
    }

    if report_filter not in allowed_filters:
        report_filter = "all"


    # ------------------------------------------------------
    # Get current campaign monitoring data
    # ------------------------------------------------------

    data = MonitoringService.get_dashboard()

    campaign = data.get("campaign")
    monitoring = data.get("monitoring", [])
    summary = data.get("summary", {})


    # ------------------------------------------------------
    # Generate workbook
    # ------------------------------------------------------

    workbook = (
        ReportService
        .create_squad_wise_workbook(
            campaign=campaign,
            monitoring=monitoring,
            summary=summary,
            report_filter=report_filter,
        )
    )


    # ------------------------------------------------------
    # Download filename
    # ------------------------------------------------------

    filter_filename = (
        report_filter
        .replace("-", "_")
    )

    filename = (
        "NCMS_Squad_Wise_"
        f"{filter_filename}.xlsx"
    )


    # ------------------------------------------------------
    # Send Excel file
    # ------------------------------------------------------

    return send_file(
        workbook,
        as_attachment=True,
        download_name=filename,
        mimetype=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

# ==========================================================
# Panchayath Achievement Excel Export
# ==========================================================

@reports_bp.route(
    "/panchayath-achievement/export"
)
def export_panchayath_achievement():

    # ------------------------------------------------------
    # Requested report category
    # ------------------------------------------------------

    report_filter = request.args.get(
        "filter",
        "all",
    ).strip().lower()


    # ------------------------------------------------------
    # Allow only known filters
    # ------------------------------------------------------

    allowed_filters = {
        "all",
        "vaccination-achieved",
        "pashudhan-achieved",
        "both-achieved",
        "low-vaccination",
        "low-pashudhan",
        "low-both",
        "pending",
    }

    if report_filter not in allowed_filters:
        report_filter = "all"


    # ------------------------------------------------------
    # Get current campaign monitoring data
    # ------------------------------------------------------

    data = MonitoringService.get_dashboard()

    campaign = data.get("campaign")
    monitoring = data.get("monitoring", [])
    summary = data.get("summary", {})


    # ------------------------------------------------------
    # Generate workbook
    # ------------------------------------------------------

    workbook = (
        ReportService
        .create_panchayath_achievement_workbook(
            campaign=campaign,
            monitoring=monitoring,
            summary=summary,
            report_filter=report_filter,
        )
    )


    # ------------------------------------------------------
    # Download filename
    # ------------------------------------------------------

    filter_filename = (
        report_filter
        .replace("-", "_")
    )

    filename = (
        "NCMS_Panchayath_Achievement_"
        f"{filter_filename}.xlsx"
    )


    # ------------------------------------------------------
    # Send Excel file
    # ------------------------------------------------------

    return send_file(
        workbook,
        as_attachment=True,
        download_name=filename,
        mimetype=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )
# ==========================================================
# Pending Submission Excel Export
# ==========================================================

@reports_bp.route("/pending-submissions/export")
def export_pending_submissions():

    # ------------------------------------------------------
    # Get current campaign monitoring data
    # ------------------------------------------------------

    data = MonitoringService.get_dashboard()

    campaign = data.get("campaign")
    monitoring = data.get("monitoring", [])
    summary = data.get("summary", {})


    # ------------------------------------------------------
    # Generate workbook
    # ------------------------------------------------------

    workbook = (
        ReportService
        .create_pending_submissions_workbook(
            campaign=campaign,
            monitoring=monitoring,
            summary=summary,
        )
    )


    # ------------------------------------------------------
    # Download filename
    # ------------------------------------------------------

    filename = (
        "NCMS_Pending_Submissions.xlsx"
    )


    # ------------------------------------------------------
    # Send Excel file
    # ------------------------------------------------------

    return send_file(
        workbook,
        as_attachment=True,
        download_name=filename,
        mimetype=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )