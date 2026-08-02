from datetime import datetime

from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:

    # ======================================================
    # MAIN DASHBOARD
    # ======================================================

    @staticmethod
    def get_dashboard():

        # --------------------------------------------------
        # Active Campaign
        # --------------------------------------------------

        campaign = DashboardRepository.get_active_campaign()

        if campaign is None:
            return {
                "campaign": None,
                "submitted": 0,
                "pending": 0,
                "total_squads": 0,
                "vaccinations": 0,
                "entries": 0,
                "target": 0,
                "vaccination_percent": 0,
                "entry_percent": 0,
                "today": 0,
                "recent_submissions": [],
            }

        # --------------------------------------------------
        # Campaign Squads
        # --------------------------------------------------

        squads = DashboardRepository.get_campaign_squads(
            campaign.id
        )

        total_squads = len(squads)

        # --------------------------------------------------
        # Target
        # --------------------------------------------------

        target = sum(
            squad.target or 0
            for squad in squads
        )

        # --------------------------------------------------
        # Campaign Submissions
        # --------------------------------------------------

        submissions = (
            DashboardRepository.get_campaign_submissions(
                campaign.id
            )
        )

        submitted = len(submissions)

        pending = max(
            total_squads - submitted,
            0
        )

        # --------------------------------------------------
        # Vaccination / Pashudhan totals
        # --------------------------------------------------

        vaccinations = sum(
            submission.vaccinations_done or 0
            for submission in submissions
        )

        entries = sum(
            submission.pashudhan_entries or 0
            for submission in submissions
        )

        # --------------------------------------------------
        # Percentages
        # --------------------------------------------------

        vaccination_percent = 0
        entry_percent = 0

        if target > 0:

            vaccination_percent = round(
                (vaccinations / target) * 100,
                2
            )

            entry_percent = round(
                (entries / target) * 100,
                2
            )

        # --------------------------------------------------
        # Today's submissions
        # --------------------------------------------------

        today = datetime.now().date()

        today_count = sum(
            1
            for submission in submissions
            if submission.submitted_at
            and submission.submitted_at.date() == today
        )

        # --------------------------------------------------
        # Recent submissions
        # --------------------------------------------------

        recent_submissions = sorted(
            submissions,
            key=lambda submission: (
                submission.submitted_at
                or submission.created_at
            ),
            reverse=True,
        )[:10]

        # --------------------------------------------------
        # Dashboard result
        # --------------------------------------------------

        return {
            "campaign": campaign,
            "submitted": submitted,
            "pending": pending,
            "total_squads": total_squads,
            "vaccinations": vaccinations,
            "entries": entries,
            "target": target,
            "vaccination_percent": vaccination_percent,
            "entry_percent": entry_percent,
            "today": today_count,
            "recent_submissions": recent_submissions,
        }


    # ======================================================
    # DASHBOARD API SUMMARY
    # ======================================================

    @staticmethod
    def get_summary():

        dashboard = DashboardService.get_dashboard()

        campaign = dashboard["campaign"]

        # --------------------------------------------------
        # No active campaign
        # --------------------------------------------------

        if campaign is None:

            return {
                "active_campaign": None,
                "submitted": 0,
                "pending": 0,
                "total_squads": 0,
                "vaccinations": 0,
                "entries": 0,
                "target": 0,
                "vaccination_percent": 0,
                "entry_percent": 0,
                "today": 0,
            }

        # --------------------------------------------------
        # JSON-safe campaign data
        # --------------------------------------------------

        campaign_data = {
            "id": campaign.id,
            "name": campaign.name,
            "code": campaign.code,
            "status": campaign.status,
        }

        # --------------------------------------------------
        # JSON-safe API result
        # --------------------------------------------------

        return {
            "active_campaign": campaign_data,
            "submitted": dashboard["submitted"],
            "pending": dashboard["pending"],
            "total_squads": dashboard["total_squads"],
            "vaccinations": dashboard["vaccinations"],
            "entries": dashboard["entries"],
            "target": dashboard["target"],
            "vaccination_percent": (
                dashboard["vaccination_percent"]
            ),
            "entry_percent": (
                dashboard["entry_percent"]
            ),
            "today": dashboard["today"],
        }