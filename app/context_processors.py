from app.models import Campaign


def inject_active_campaign():
    active_campaign = (
        Campaign.query.filter_by(is_active=True)
        .order_by(Campaign.id.desc())
        .first()
    )

    return {
        "active_campaign": active_campaign
    }