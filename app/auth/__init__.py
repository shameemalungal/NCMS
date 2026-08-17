from flask import Blueprint


# ==========================================================
# Authentication Blueprint
# ==========================================================

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)


# ==========================================================
# Authentication Models
#
# Importing the models here ensures SQLAlchemy/Alembic
# discovers the RBAC models when the application starts.
# ==========================================================

from app.auth.models import (  # noqa: E402,F401
    User,
    Role,
    Permission,
    user_roles,
    role_permissions,
)


# ==========================================================
# Authentication Routes
# ==========================================================

from app.auth import routes  # noqa: E402,F401