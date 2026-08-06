from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect


# ==========================================================
# Database
# ==========================================================

db = SQLAlchemy()


# ==========================================================
# Database Migrations
# ==========================================================

migrate = Migrate()


# ==========================================================
# CSRF Protection
# ==========================================================

csrf = CSRFProtect()