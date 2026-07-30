from pathlib import Path

from flask import Flask

from config import Config
from app.extensions import db, migrate

from app.dashboard import dashboard_bp
from app.submission import submission_bp
from app.campaign import campaign_bp
from app.masterdata import masterdata_bp
from app.panchayath import panchayath_bp
from app.reports import reports_bp


BASE_DIR = Path(__file__).resolve().parent.parent


def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(submission_bp)
    app.register_blueprint(campaign_bp)
    app.register_blueprint(masterdata_bp)
    app.register_blueprint(panchayath_bp)
    app.register_blueprint(reports_bp)

    return app
