from flask import render_template

from app.audit import audit_bp
from app.auth.decorators import admin_required
from app.models import AuditLog


@audit_bp.route("/")
@admin_required
def index():

    logs = (
        AuditLog.query
        .order_by(
            AuditLog.created_at.desc()
        )
        .limit(500)
        .all()
    )

    return render_template(
        "audit/index.html",
        logs=logs,
        page_title="Audit Logs",
    )
