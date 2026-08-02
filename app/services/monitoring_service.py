from app.models import (
    Campaign,
    Panchayath,
    Squad,
    Submission,
)


class MonitoringService:

    @staticmethod
    def get_dashboard():

        campaign = Campaign.query.filter_by(
            is_active=True
        ).first()

        if campaign is None:

            return {

                "campaign": None,

                "monitoring": []

            }

        monitoring = []

        panchayaths = Panchayath.query.filter_by(
            campaign_id=campaign.id
        ).all()

        for p in panchayaths:

            squads = Squad.query.filter_by(
                panchayath_id=p.id
            ).all()

            total = len(squads)

            submitted = 0

            target = 0

            vaccinations = 0

            entries = 0

            pending_squads = []

            for squad in squads:

                target += squad.target or 0

                submission = Submission.query.filter_by(
                    squad_id=squad.id
                ).first()

                if submission:

                    submitted += 1

                    vaccinations += (
                        submission.vaccinations_done or 0
                    )

                    entries += (
                        submission.pashudhan_entries or 0
                    )

                else:

                    pending_squads.append(squad)

            pending = total - submitted

            achievement = 0

            if target:

                achievement = round(
                    vaccinations * 100 / target,
                    2
                )

            monitoring.append({

                "panchayath": p,

                "total": total,

                "submitted": submitted,

                "pending": pending,

                "vaccinations": vaccinations,

                "entries": entries,

                "target": target,

                "achievement": achievement,

                "pending_squads": pending_squads,

            })

        monitoring.sort(
            key=lambda x: x["achievement"],
            reverse=True
        )

        return {

            "campaign": campaign,

            "monitoring": monitoring

        }