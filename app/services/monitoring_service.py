from sqlalchemy import func

from app.extensions import db
from app.models import (
    Campaign,
    Panchayath,
    Squad,
    Submission,
)


class MonitoringService:
    """
    Service responsible for district, Panchayath and squad-level
    monitoring of the active NADCP campaign.
    """

    # ==========================================================
    # Achievement Targets
    # ==========================================================

    VACCINATION_TARGET = 83.0
    PASHUDHAN_TARGET = 97.0


    # ==========================================================
    # Helper: Squad Members
    # ==========================================================

    @staticmethod
    def _get_squad_members(squad):
        """
        Convert SquadMember model objects into dictionaries that
        can safely be used by the monitoring template and search.
        """

        members = []

        for member in squad.members:

            members.append(
                {
                    "id": member.id,
                    "member_name": member.member_name or "",
                    "office": member.office or "",
                    "pashudhan_id": member.pashudhan_id or "",
                }
            )

        return members


    # ==========================================================
    # Main Monitoring Dashboard
    # ==========================================================

    @staticmethod
    def get_dashboard():

        # ------------------------------------------------------
        # Active Campaign
        # ------------------------------------------------------

        campaign = (
            Campaign.query
            .filter_by(is_active=True)
            .first()
        )

        if not campaign:

            return {
                "campaign": None,
                "monitoring": [],
                "summary": {
                    "panchayaths": 0,
                    "total_squads": 0,
                    "submitted_squads": 0,
                    "pending_squads": 0,
                    "target": 0,
                    "vaccinations": 0,
                    "entries": 0,
                    "vaccination_percentage": 0.0,
                    "pashudhan_percentage": 0.0,
                    "vaccination_target":
                        MonitoringService.VACCINATION_TARGET,
                    "pashudhan_target":
                        MonitoringService.PASHUDHAN_TARGET,
                },
            }


        # ======================================================
        # DISTRICT TOTALS
        # ======================================================

        panchayaths = (
            Panchayath.query
            .filter_by(campaign_id=campaign.id)
            .order_by(Panchayath.name)
            .all()
        )

        total_panchayaths = len(panchayaths)


        # ------------------------------------------------------
        # Total Squads
        # ------------------------------------------------------

        total_squads = (
            Squad.query
            .filter_by(campaign_id=campaign.id)
            .count()
        )


        # ------------------------------------------------------
        # Submitted Squads
        #
        # Count actual Submission records.
        # ------------------------------------------------------

        submitted_squads = (
            db.session.query(
                func.count(Submission.id)
            )
            .select_from(Submission)
            .join(
                Squad,
                Submission.squad_id == Squad.id,
            )
            .filter(
                Squad.campaign_id == campaign.id
            )
            .scalar()
            or 0
        )

        pending_squads = max(
            total_squads - submitted_squads,
            0,
        )


        # ------------------------------------------------------
        # District Population Target
        #
        # Panchayath.population is the campaign population.
        # Squad.target is an allocation of that population.
        # ------------------------------------------------------

        district_target = (
            db.session.query(
                func.coalesce(
                    func.sum(Panchayath.population),
                    0,
                )
            )
            .filter(
                Panchayath.campaign_id == campaign.id
            )
            .scalar()
            or 0
        )


        # ------------------------------------------------------
        # District Vaccinations
        # ------------------------------------------------------

        district_vaccinations = (
            db.session.query(
                func.coalesce(
                    func.sum(
                        Submission.vaccinations_done
                    ),
                    0,
                )
            )
            .select_from(Submission)
            .join(
                Squad,
                Submission.squad_id == Squad.id,
            )
            .filter(
                Squad.campaign_id == campaign.id
            )
            .scalar()
            or 0
        )


        # ------------------------------------------------------
        # District Pashudhan Entries
        # ------------------------------------------------------

        district_entries = (
            db.session.query(
                func.coalesce(
                    func.sum(
                        Submission.pashudhan_entries
                    ),
                    0,
                )
            )
            .select_from(Submission)
            .join(
                Squad,
                Submission.squad_id == Squad.id,
            )
            .filter(
                Squad.campaign_id == campaign.id
            )
            .scalar()
            or 0
        )


        # ======================================================
        # DISTRICT ACHIEVEMENT
        #
        # Vaccination Achievement:
        # Vaccinations / Population × 100
        #
        # Pashudhan Achievement:
        # Pashudhan Entries / Population × 100
        # ======================================================

        if district_target:

            district_vaccination_percentage = round(
                (
                    district_vaccinations
                    / district_target
                )
                * 100,
                2,
            )

            district_pashudhan_percentage = round(
                (
                    district_entries
                    / district_target
                )
                * 100,
                2,
            )

        else:

            district_vaccination_percentage = 0.0
            district_pashudhan_percentage = 0.0


        # ======================================================
        # PANCHAYATH MONITORING
        # ======================================================

        monitoring = []

        for panchayath in panchayaths:

            # --------------------------------------------------
            # Panchayath Squads
            # --------------------------------------------------

            squads = (
                Squad.query
                .filter_by(
                    campaign_id=campaign.id,
                    panchayath_id=panchayath.id,
                )
                .order_by(Squad.squad_no)
                .all()
            )

            total = len(squads)

            target = panchayath.population or 0


            # --------------------------------------------------
            # Panchayath Counters
            # --------------------------------------------------

            submitted = 0

            panchayath_vaccinations = 0
            panchayath_entries = 0

            submitted_squad_details = []
            pending_squad_details = []


            # ==================================================
            # PROCESS EACH SQUAD
            # ==================================================

            for squad in squads:

                # ----------------------------------------------
                # Squad Members
                # ----------------------------------------------

                members = (
                    MonitoringService
                    ._get_squad_members(squad)
                )


                # ----------------------------------------------
                # Submission
                # ----------------------------------------------

                submission = (
                    Submission.query
                    .filter_by(squad_id=squad.id)
                    .order_by(
                        Submission.submitted_at.desc()
                    )
                    .first()
                )


                # ==============================================
                # PENDING SQUAD
                # ==============================================
                if not submission:
                
                    pending_squad_details.append(
                        {
                            "id":
                                squad.id,
                
                            "squad_no":
                                squad.squad_no,
                
                            "squad_days":
                                squad.squad_days or 0,
                
                            "target":
                                squad.target or 0,
                
                            "status":
                                "Pending",
                
                            "members":
                                members,
                        }
                    )
                
                    continue
                                


                # ==============================================
                # SUBMITTED SQUAD
                # ==============================================

                submitted += 1

                vaccinations = (
                    submission.vaccinations_done
                    or 0
                )

                entries = (
                    submission.pashudhan_entries
                    or 0
                )

                squad_target = (
                    squad.target
                    or 0
                )

                panchayath_vaccinations += vaccinations
                panchayath_entries += entries


                # ----------------------------------------------
                # Squad Vaccination Achievement
                # ----------------------------------------------

                if squad_target:

                    squad_vaccination_percentage = round(
                        (
                            vaccinations
                            / squad_target
                        )
                        * 100,
                        2,
                    )

                else:

                    squad_vaccination_percentage = 0.0


                # ----------------------------------------------
                # Squad Pashudhan Achievement
                #
                # Pashudhan Entries / Squad Population Target
                # ----------------------------------------------

                if squad_target:

                    squad_pashudhan_percentage = round(
                        (
                            entries
                            / squad_target
                        )
                        * 100,
                        2,
                    )

                else:

                    squad_pashudhan_percentage = 0.0


                # ----------------------------------------------
                # Squad Achievement Flags
                # ----------------------------------------------

                squad_vaccination_target_met = (
                    squad_vaccination_percentage
                    >= MonitoringService.VACCINATION_TARGET
                )

                squad_pashudhan_target_met = (
                    squad_pashudhan_percentage
                    >= MonitoringService.PASHUDHAN_TARGET
                )


                # ----------------------------------------------
                # Squad Status
                # ----------------------------------------------

                if (
                    squad_vaccination_target_met
                    and squad_pashudhan_target_met
                ):

                    squad_status = "Target Achieved"

                elif (
                    not squad_vaccination_target_met
                    and not squad_pashudhan_target_met
                ):

                    squad_status = "Low Both"

                elif not squad_vaccination_target_met:

                    squad_status = "Low Vaccination"

                else:

                    squad_status = "Low Pashudhan"


                # ----------------------------------------------
                # Submitted Squad Record
                # ----------------------------------------------

                submitted_squad_details.append(
                    {
                        "id":
                            squad.id,

                        "squad_no":
                            squad.squad_no,

                        "squad_days":
                            squad.squad_days or 0,

                        "target":
                            squad_target,

                        "status":
                            squad_status,

                        "members":
                            members,

                        "vaccinations":
                            vaccinations,

                        "entries":
                            entries,

                        "vaccination_percentage":
                            squad_vaccination_percentage,

                        "pashudhan_percentage":
                            squad_pashudhan_percentage,

                        "vaccination_target_met":
                            squad_vaccination_target_met,

                        "pashudhan_target_met":
                            squad_pashudhan_target_met,

                        "submission_token":
                            getattr(
                                submission,
                                "submission_token",
                                None,
                            ),

                        "vaccination_reason":
                            getattr(
                                submission,
                                "vaccination_reason",
                                None,
                            ),

                        "pashudhan_reason":
                            getattr(
                                submission,
                                "pashudhan_reason",
                                None,
                            ),

                        "submitted_at":
                            submission.submitted_at,
                    }
                )


            # ==================================================
            # PANCHAYATH ACHIEVEMENT
            #
            # Vaccination %:
            # Vaccinations / Panchayath Population × 100
            #
            # Pashudhan %:
            # Entries / Panchayath Population × 100
            # ==================================================

            if target:

                vaccination_percentage = round(
                    (
                        panchayath_vaccinations
                        / target
                    )
                    * 100,
                    2,
                )

                pashudhan_percentage = round(
                    (
                        panchayath_entries
                        / target
                    )
                    * 100,
                    2,
                )

            else:

                vaccination_percentage = 0.0
                pashudhan_percentage = 0.0


            # --------------------------------------------------
            # Panchayath Target Flags
            # --------------------------------------------------

            vaccination_target_met = (
                vaccination_percentage
                >= MonitoringService.VACCINATION_TARGET
            )

            pashudhan_target_met = (
                pashudhan_percentage
                >= MonitoringService.PASHUDHAN_TARGET
            )


            # --------------------------------------------------
            # Pending
            # --------------------------------------------------

            pending = max(
                total - submitted,
                0,
            )


            # ==================================================
            # PANCHAYATH STATUS
            #
            # A Panchayath remains Pending until every squad
            # has submitted.
            # ==================================================

            if submitted == 0:

                status = "Not Started"

            elif pending > 0:

                status = "Pending"

            elif (
                vaccination_target_met
                and pashudhan_target_met
            ):

                status = "Target Achieved"

            elif (
                not vaccination_target_met
                and not pashudhan_target_met
            ):

                status = "Low Both"

            elif not vaccination_target_met:

                status = "Low Vaccination"

            else:

                status = "Low Pashudhan"


            # ==================================================
            # SEARCH TEXT
            #
            # Build one searchable string containing:
            #
            # - Panchayath
            # - Squad numbers
            # - Member names
            # - Offices
            # - Pashudhan IDs
            # - Submission references
            #
            # The HTML/JavaScript can use this for instant search.
            # ==================================================

            search_parts = [
                panchayath.name or "",
            ]


            # --------------------------------------------------
            # Submitted Squads Search Data
            # --------------------------------------------------

            for squad_data in submitted_squad_details:

                search_parts.append(
                    str(
                        squad_data["squad_no"]
                    )
                )

                if squad_data["submission_token"]:

                    search_parts.append(
                        squad_data[
                            "submission_token"
                        ]
                    )

                for member in squad_data["members"]:

                    search_parts.extend(
                        [
                            member["member_name"],
                            member["office"],
                            member["pashudhan_id"],
                        ]
                    )


            # --------------------------------------------------
            # Pending Squads Search Data
            # --------------------------------------------------

            for squad_data in pending_squad_details:

                search_parts.append(
                    str(
                        squad_data["squad_no"]
                    )
                )

                for member in squad_data["members"]:

                    search_parts.extend(
                        [
                            member["member_name"],
                            member["office"],
                            member["pashudhan_id"],
                        ]
                    )


            search_text = " ".join(
                str(value)
                for value in search_parts
                if value
            )


            # ==================================================
            # ADD PANCHAYATH RECORD
            # ==================================================

            monitoring.append(
                {
                    "panchayath":
                        panchayath,

                    "total":
                        total,

                    "submitted":
                        submitted,

                    "pending":
                        pending,

                    "target":
                        target,

                    "vaccinations":
                        panchayath_vaccinations,

                    "entries":
                        panchayath_entries,

                    # Kept for compatibility
                    "achievement":
                        vaccination_percentage,

                    "vaccination_percentage":
                        vaccination_percentage,

                    "pashudhan_percentage":
                        pashudhan_percentage,

                    "vaccination_target_met":
                        vaccination_target_met,

                    "pashudhan_target_met":
                        pashudhan_target_met,

                    "status":
                        status,

                    "submitted_squads":
                        submitted_squad_details,

                    "pending_squads":
                        pending_squad_details,

                    "search_text":
                        search_text,
                }
            )


        # ======================================================
        # SORT PANCHAYATH MONITORING
        #
        # Panchayaths with the most submissions appear first.
        # Alphabetical order is used when submission counts match.
        # ======================================================

        monitoring.sort(
            key=lambda row: (
                -row["submitted"],
                row["panchayath"].name.lower(),
            )
        )


        # ======================================================
        # DISTRICT SUMMARY
        # ======================================================

        summary = {
            "panchayaths":
                total_panchayaths,

            "total_squads":
                total_squads,

            "submitted_squads":
                submitted_squads,

            "pending_squads":
                pending_squads,

            "target":
                district_target,

            "vaccinations":
                district_vaccinations,

            "entries":
                district_entries,

            "vaccination_percentage":
                district_vaccination_percentage,

            "pashudhan_percentage":
                district_pashudhan_percentage,

            "vaccination_target":
                MonitoringService.VACCINATION_TARGET,

            "pashudhan_target":
                MonitoringService.PASHUDHAN_TARGET,
        }


        # ======================================================
        # FINAL RESULT
        # ======================================================

        return {
            "campaign":
                campaign,

            "monitoring":
                monitoring,

            "summary":
                summary,
        }