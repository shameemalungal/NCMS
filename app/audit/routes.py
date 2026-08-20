from flask import render_template

from app.audit import audit_bp
from app.auth.decorators import require_permission
from app.models import AuditLog


@audit_bp.route("/")
@require_permission("audit.view")
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
