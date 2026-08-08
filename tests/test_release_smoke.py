import os

import pytest

os.environ.setdefault("NCMS_ENVIRONMENT", "testing")
os.environ.setdefault("NCMS_SECRET_KEY", "test-secret-key")
os.environ.setdefault("NCMS_ADMIN_USERNAME", "test-admin")
os.environ.setdefault("NCMS_ADMIN_PASSWORD", "test-password")

from app import create_app
from app.extensions import db
from app.models import Campaign, Panchayath, Squad, Submission


@pytest.fixture()
def app():
    app = create_app()

    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    assert response.get_json()["database"] == "ok"


def test_public_submission_page_without_campaign(client):
    response = client.get("/submit/")

    assert response.status_code == 200
    assert b"No Active Campaign" in response.data


def test_admin_pages_are_protected(client):
    response = client.get("/settings/")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_admin_login_and_settings_access(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "test-admin",
            "password": "test-password",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    response = client.get("/settings/")
    assert response.status_code == 200


def test_public_submission_uses_only_active_campaign(client, app):
    with app.app_context():
        inactive = Campaign(
            name="Inactive Campaign",
            code="INACTIVE",
            is_active=False,
            submissions_open=True,
        )

        active = Campaign(
            name="Active Campaign",
            code="ACTIVE",
            is_active=True,
            submissions_open=True,
        )

        db.session.add_all([inactive, active])
        db.session.flush()

        panchayath = Panchayath(
            campaign_id=active.id,
            name="Test Panchayath",
            population=100,
        )

        db.session.add(panchayath)
        db.session.flush()

        squad = Squad(
            campaign_id=active.id,
            panchayath_id=panchayath.id,
            squad_no=1,
            squad_days=2,
            target=100,
        )

        db.session.add(squad)
        db.session.commit()

    response = client.get("/submit/")

    assert response.status_code == 200
    assert b"Active Campaign" in response.data
    assert b"Inactive Campaign" not in response.data
    assert b"Test Panchayath" in response.data


def test_closed_campaign_blocks_public_submission(client, app):
    with app.app_context():
        campaign = Campaign(
            name="Closed Campaign",
            code="CLOSED",
            is_active=True,
            submissions_open=False,
        )

        db.session.add(campaign)
        db.session.flush()

        panchayath = Panchayath(
            campaign_id=campaign.id,
            name="Closed Panchayath",
            population=100,
        )

        db.session.add(panchayath)
        db.session.flush()

        squad = Squad(
            campaign_id=campaign.id,
            panchayath_id=panchayath.id,
            squad_no=1,
            squad_days=1,
            target=100,
        )

        db.session.add(squad)
        db.session.commit()
        squad_id = squad.id

    response = client.get(f"/submit/form/{squad_id}")

    assert response.status_code == 200
    assert b"Submissions Closed" in response.data


def test_duplicate_submission_is_blocked(client, app):
    with app.app_context():
        campaign = Campaign(
            name="Duplicate Test",
            code="DUP",
            is_active=True,
            submissions_open=True,
        )

        db.session.add(campaign)
        db.session.flush()

        panchayath = Panchayath(
            campaign_id=campaign.id,
            name="Duplicate Panchayath",
            population=100,
        )

        db.session.add(panchayath)
        db.session.flush()

        squad = Squad(
            campaign_id=campaign.id,
            panchayath_id=panchayath.id,
            squad_no=1,
            squad_days=1,
            target=100,
        )

        db.session.add(squad)
        db.session.flush()

        submission = Submission(
            squad_id=squad.id,
            submission_token="DUP-TEST01",
            submitted_at=db.func.now(),
        )

        db.session.add(submission)
        db.session.commit()
        squad_id = squad.id

    response = client.get(f"/submit/form/{squad_id}")

    assert response.status_code == 200
    assert b"Already Submitted" in response.data
