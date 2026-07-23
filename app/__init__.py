from pathlib import Path
from flask import Flask

from config import Config
from app.extensions import db, migrate

BASE_DIR = Path(__file__).resolve().parent.parent


def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models
    from app import models

    # Register blueprints
    from app.dashboard import dashboard_bp
    from app.masterdata import masterdata_bp
    from app.submission import submission_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(masterdata_bp)
    app.register_blueprint(submission_bp)

    return app