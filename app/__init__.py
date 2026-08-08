from pathlib import Path

from flask import Flask, jsonify
from sqlalchemy import text

from config import Config
from app.extensions import db, migrate, csrf


# Blueprints
from app.dashboard import dashboard_bp
from app.dashboard.api import bp as dashboard_api_bp
from app.submission import submission_bp
from app.campaign import campaign_bp
from app.masterdata import masterdata_bp
from app.panchayath import panchayath_bp
from app.reports import reports_bp
from app.monitoring import monitoring_bp
from app.settings import settings_bp
from app.auth import auth_bp
from app.audit import audit_bp
from app.backup import backup_bp


BASE_DIR = Path(__file__).resolve().parent.parent


def create_app():

    # ======================================================
    # Flask Application
    # ======================================================

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    # ======================================================
    # Configuration
    # ======================================================

    app.config.from_object(Config)

    # ======================================================
    # Extensions
    # ======================================================

    db.init_app(app)

    migrate.init_app(
        app,
        db,
    )

    csrf.init_app(app)

    # ======================================================
    # Register Blueprints
    # ======================================================

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(dashboard_api_bp)
    app.register_blueprint(campaign_bp)
    app.register_blueprint(masterdata_bp)
    app.register_blueprint(submission_bp)
    app.register_blueprint(panchayath_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(backup_bp)

    # ======================================================
    # Health Check
    # ======================================================

    @app.get("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({
                "status": "ok",
                "database": "ok",
            }), 200
        except Exception:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "database": "unavailable",
            }), 503

    # ======================================================
    # Context Processors
    # ======================================================

    from app.context_processors import (
        inject_active_campaign,
    )

    app.context_processor(
        inject_active_campaign
    )

    # ======================================================
    # Return Application
    # ======================================================

    return app
