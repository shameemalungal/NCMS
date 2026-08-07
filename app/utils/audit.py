from flask import request

from app.extensions import db
from app.models import AuditLog


def log_audit(
    username,
    module,
    action,
):

    try:

        entry = AuditLog(
            username=username,
            module=module,
            action=action,
            ip_address=request.remote_addr,
        )

        db.session.add(entry)
        db.session.commit()

    except Exception:

        db.session.rollback()