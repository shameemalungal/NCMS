# NCMS

**NADCP Campaign Management System**

NCMS is a Flask-based campaign management application for vaccination campaign master-data management, public squad submissions, monitoring, reports, audit logging and administrative backup/export.

## Current release

- Version: **1.0 Release Candidate 1**
- Tag: `ncms-v1.0-rc1`
- Stable branch: `main`

## Core modules

- Administrator authentication
- Campaign management
- Master data import and validation
- Public squad submission
- District, Panchayath and Squad monitoring
- Reports and Excel exports
- Settings and public submission controls
- Audit log
- Administrator backup export

## Local development

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run database migrations:

```powershell
flask db upgrade
```

Run the development server:

```powershell
flask run
```

Health check:

```text
http://127.0.0.1:5000/health
```

## Production configuration

Copy `.env.example` to your deployment environment and set real values. Never commit production secrets.

At minimum configure:

```text
NCMS_ENVIRONMENT=production
NCMS_SECRET_KEY=<long-random-secret>
NCMS_ADMIN_USERNAME=<administrator-username>
NCMS_ADMIN_PASSWORD=<strong-unique-password>
NCMS_SESSION_COOKIE_SECURE=true
NCMS_TRUSTED_HOSTS=<production-hostname>
```

The application can use `DATABASE_URL` when a production database is available. Without it, the application falls back to SQLite at `database/ncms.db`.

## Production server

The repository includes a `Procfile` using Gunicorn:

```text
web: gunicorn 'app:create_app()'
```

For Render, `render.yaml` provides the production web-service configuration and health check.

## Testing

Install development dependencies:

```powershell
pip install -r requirements-dev.txt
```

Run the release smoke tests:

```powershell
python -m pytest -q
```

## Release validation

See [`PUBLIC_RELEASE_CHECKLIST.md`](PUBLIC_RELEASE_CHECKLIST.md) for the complete pre-deployment, data-validation, backup, mobile-testing, pilot and final-release checklist.

## Security notes

- Administrator pages use session-based authentication.
- Administrative forms are protected with Flask-WTF CSRF protection.
- Public submission endpoints do not require administrator login.
- Administrator backup download requires authentication.
- Production secrets are read from environment variables.
- Production debug mode is disabled.
- Session cookies are HTTP-only and SameSite protected, with Secure enabled for production by default.

## License

Internal application. Add the organization's approved licensing terms before public source distribution.
