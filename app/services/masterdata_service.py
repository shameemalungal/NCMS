import re
import secrets

from app.extensions import db
from app.models import (
    Campaign,
    Panchayath,
    Squad,
    SquadMember,
    ImportHistory,
)

from app.utils.excel_reader import ExcelReader
from app.utils.validators import WorkbookValidator


class MasterDataImporter:

    def __init__(self, filepath):
        self.filepath = filepath
        self.reader = ExcelReader(filepath)

        self.campaign = None

        self.panchayaths = {}
        self.squads = {}

    def import_data(self):

        self.reader.load()
        self.reader.validate()

        rows = self.reader.get_squad_rows()

        errors = WorkbookValidator.validate_rows(rows)

        if errors:
            raise Exception("\n".join(errors))

        population = self.reader.get_population()

        try:

            self.create_campaign()

            self.import_panchayaths(rows, population)

            self.import_squads(rows)

            self.import_members(rows)

            self.create_import_history()

            db.session.commit()

        except Exception:

            db.session.rollback()

            raise

    ##############################################################

    def create_campaign(self):

        campaign = Campaign(
            name="NADCP 8",
            code="NADCP8",
            status="OPEN",
            is_active=True,
        )

        db.session.add(campaign)
        db.session.flush()

        self.campaign = campaign

    ##############################################################

    def import_panchayaths(self, rows, population):

        unique_names = sorted(
            {
                row["panchayath"]
                for row in rows
            }
        )

        for name in unique_names:

            p = Panchayath(
                campaign_id=self.campaign.id,
                name=name,
                population=population.get(name, 0),
            )

            db.session.add(p)
            db.session.flush()

            self.panchayaths[name] = p

    ##############################################################

    def import_squads(self, rows):

        for row in rows:

            key = (
                row["panchayath"],
                row["squad_no"],
            )

            if key in self.squads:
                continue

            panchayath = self.panchayaths[row["panchayath"]]

            squad = Squad(
                campaign_id=self.campaign.id,
                panchayath_id=panchayath.id,
                squad_no=row["squad_no"],
                squad_days=row["days"],
                target=panchayath.population or 0,
                submission_token=secrets.token_hex(16),
                status="PENDING",
            )

            db.session.add(squad)
            db.session.flush()

            self.squads[key] = squad

    ##############################################################

    def import_members(self, rows):

        for row in rows:

            key = (
                row["panchayath"],
                row["squad_no"],
            )

            squad = self.squads[key]

            full_text = row["member"]

            member_name = full_text
            office = ""

            m = re.match(
                r"^(.*?)\((.*?)\)$",
                full_text,
            )

            if m:
                member_name = m.group(1).strip()
                office = m.group(2).strip()

            member = SquadMember(
                squad_id=squad.id,
                member_name=member_name,
                office=office,
                pashudhan_id=row["pashudhan_id"],
                full_text=full_text,
            )

            db.session.add(member)

    ##############################################################

    def create_import_history(self):

        history = ImportHistory(
            campaign_id=self.campaign.id,
            filename=self.filepath.split("\\")[-1],
            status="SUCCESS",
        )

        db.session.add(history)