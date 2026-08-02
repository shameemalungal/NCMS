from flask import Blueprint


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
)


# Import routes AFTER creating the blueprint.
# This is required so the @dashboard_bp.route(...)
# decorators are executed and registered.
from . import routes