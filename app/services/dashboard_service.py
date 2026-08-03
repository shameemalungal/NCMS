from datetime import datetime

from app.repositories.dashboard_repository import (
    DashboardRepository,
)


class DashboardService:

    # ======================================================
    # MAIN DASHBOARD
    # ======================================================

    @staticmethod
    def get_dashboard():

        # --------------------------------------------------
        # Active Campaign
        # --------------------------------------------------

        campaign = (
            DashboardRepository
            .get_active_campaign()
        )

        if campaign is None:

            return {
                "active_campaign": None,
                "submitted_squads": 0,
                "pending_squads": 0,
                "total_squads": 0,
                "total_vaccinations": 0,
                "total_entries": 0,
                "total_leftover": 0,
                "target": 0,
                "vaccination_percentage": 0,
                "vaccine_coverage_percentage": 0,
                "pashudhan_percentage": 0,
                "today_submissions": 0,
                "recent_submissions": [],
            }

        # --------------------------------------------------
        # Campaign Squads
        # --------------------------------------------------

        squads = (
            DashboardRepository
            .get_campaign_squads(
                campaign.id
            )
        )

        total_squads = len(squads)

        # --------------------------------------------------
        # Campaign Target
        # --------------------------------------------------

        target = sum(
            squad.target or 0
            for squad in squads
        )

        # --------------------------------------------------
        # Campaign Submissions
        # --------------------------------------------------

        submissions = (
            DashboardRepository
            .get_campaign_submissions(
                campaign.id
            )
        )

        submitted_squads = len(
            submissions
        )

        pending_squads = max(
            total_squads
            - submitted_squads,
            0,
        )

        # --------------------------------------------------
        # Vaccination Total
        # --------------------------------------------------

        total_vaccinations = sum(
            submission.vaccinations_done or 0
            for submission in submissions
        )

        # --------------------------------------------------
        # Pashudhan Entry Total
        # --------------------------------------------------

        total_entries = sum(
            submission.pashudhan_entries or 0
            for submission in submissions
        )

        # --------------------------------------------------
        # Total Leftover
        # --------------------------------------------------

        total_leftover = sum(
            (
                (submission.diseased or 0)
                + (submission.below_4_months or 0)
                + (submission.pregnant or 0)
                + (submission.unwilling or 0)
                + (submission.other_count or 0)
            )
            for submission in submissions
        )

        # --------------------------------------------------
        # Achievement Percentages
        # --------------------------------------------------

        vaccination_percentage = 0
        pashudhan_percentage = 0
        vaccine_coverage_percentage = 0

        if target > 0:

            vaccination_percentage = round(
                (
                    total_vaccinations
                    / target
                )
                * 100,
                2,
            )

            pashudhan_percentage = round(
                (
                    total_entries
                    / target
                )
                * 100,
                2,
            )

            vaccine_coverage_percentage = round(
                (
                    (
                        total_vaccinations
                        + total_leftover
                    )
                    / target
                )
                * 100,
                2,
            )

        # --------------------------------------------------
        # Today's Submissions
        # --------------------------------------------------

        today = datetime.now().date()

        today_submissions = sum(
            1
            for submission in submissions
            if submission.submitted_at
            and (
                submission
                .submitted_at
                .date()
                == today
            )
        )

        # --------------------------------------------------
        # Recent Submissions
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
        # Dashboard Result
        # --------------------------------------------------

        return {
            "active_campaign": campaign,
            "submitted_squads": (
                submitted_squads
            ),
            "pending_squads": (
                pending_squads
            ),
            "total_squads": (
                total_squads
            ),
            "total_vaccinations": (
                total_vaccinations
            ),
            "total_entries": (
                total_entries
            ),
            "target": (
                target
            ),
            "vaccination_percentage": (
                vaccination_percentage
            ),
            "pashudhan_percentage": (
                pashudhan_percentage
            ),
            "today_submissions": (
                today_submissions
            ),
            "recent_submissions": (
                recent_submissions
            ),
            "total_leftover": total_leftover,
            "vaccine_coverage_percentage": (
                vaccine_coverage_percentage
            ),
        }


    # ======================================================
    # DASHBOARD API SUMMARY
    # ======================================================

    @staticmethod
    def get_summary():

        dashboard = (
            DashboardService
            .get_dashboard()
        )

        campaign = dashboard[
            "active_campaign"
        ]

        # --------------------------------------------------
        # No Active Campaign
        # --------------------------------------------------

        if campaign is None:

            return {
                "active_campaign": None,
                "submitted_squads": 0,
                "pending_squads": 0,
                "total_squads": 0,
                "total_vaccinations": 0,
                "total_entries": 0,
                "target": 0,
                "vaccination_percentage": 0,
                "pashudhan_percentage": 0,
                "today_submissions": 0,
            }

        # --------------------------------------------------
        # JSON-safe Campaign
        # --------------------------------------------------

        campaign_data = {
            "id": campaign.id,
            "name": campaign.name,
            "code": campaign.code,
            "status": campaign.status,
        }

        # --------------------------------------------------
        # JSON-safe API Result
        # --------------------------------------------------

        return {
            "active_campaign": (
                campaign_data
            ),
            "submitted_squads": (
                dashboard[
                    "submitted_squads"
                ]
            ),
            "pending_squads": (
                dashboard[
                    "pending_squads"
                ]
            ),
            "total_squads": (
                dashboard[
                    "total_squads"
                ]
            ),
            "total_vaccinations": (
                dashboard[
                    "total_vaccinations"
                ]
            ),
            "total_entries": (
                dashboard[
                    "total_entries"
                ]
            ),
            "target": (
                dashboard[
                    "target"
                ]
            ),
            "vaccination_percentage": (
                dashboard[
                    "vaccination_percentage"
                ]
            ),
            "pashudhan_percentage": (
                dashboard[
                    "pashudhan_percentage"
                ]
            ),
            "today_submissions": (
                dashboard[
                    "today_submissions"
                ]
            ),
        }