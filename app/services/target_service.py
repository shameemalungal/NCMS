from app.extensions import db
from app.models import Panchayath, Squad


class TargetService:
    """
    Handles distribution of Panchayath population
    among the squads assigned to that Panchayath.

    Business rule:

        Panchayath Population
        ---------------------
        Number of Squads

    Any remainder is distributed one-by-one among
    the first squads, ordered by squad number.

    This guarantees that the sum of squad targets
    exactly equals the Panchayath population.
    """

    @staticmethod
    def distribute_panchayath_target(panchayath_id, commit=True):

        panchayath = db.session.get(
            Panchayath,
            panchayath_id
        )

        if panchayath is None:
            raise ValueError(
                f"Panchayath {panchayath_id} not found."
            )

        # Get squads in a predictable order
        squads = (
            Squad.query
            .filter_by(
                panchayath_id=panchayath.id,
                campaign_id=panchayath.campaign_id,
            )
            .order_by(Squad.squad_no.asc())
            .all()
        )

        squad_count = len(squads)

        # No squads means there is nothing to distribute
        if squad_count == 0:
            return {
                "panchayath_id": panchayath.id,
                "panchayath": panchayath.name,
                "population": panchayath.population or 0,
                "squad_count": 0,
                "allocated_total": 0,
                "targets": [],
            }

        population = max(
            int(panchayath.population or 0),
            0
        )

        # Whole-number base target
        base_target = population // squad_count

        # Population left after equal division
        remainder = population % squad_count

        targets = []

        for index, squad in enumerate(squads):

            # Give one extra animal to the first
            # 'remainder' number of squads
            squad_target = base_target

            if index < remainder:
                squad_target += 1

            squad.target = squad_target

            targets.append({
                "squad_id": squad.id,
                "squad_no": squad.squad_no,
                "target": squad_target,
            })

        if commit:
            db.session.commit()

        return {
            "panchayath_id": panchayath.id,
            "panchayath": panchayath.name,
            "population": population,
            "squad_count": squad_count,
            "allocated_total": sum(
                item["target"]
                for item in targets
            ),
            "targets": targets,
        }


    @staticmethod
    def recalculate_campaign_targets(
        campaign_id,
        commit=True,
    ):
        """
        Recalculate targets for every Panchayath
        belonging to one campaign.
        """

        panchayaths = (
            Panchayath.query
            .filter_by(campaign_id=campaign_id)
            .order_by(Panchayath.name.asc())
            .all()
        )

        results = []

        for panchayath in panchayaths:

            result = (
                TargetService
                .distribute_panchayath_target(
                    panchayath.id,
                    commit=False,
                )
            )

            results.append(result)

        if commit:
            db.session.commit()

        return results