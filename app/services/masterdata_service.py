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

        print("=" * 80)
        print("MASTER DATA IMPORT STARTED")
        print("=" * 80)

        self.reader.load()
        print("Workbook Loaded")

        self.reader.validate()
        print("Workbook Validated")

        rows = self.reader.get_squad_rows()

        print(f"Rows Found : {len(rows)}")

        if rows:
            print("First Row :", rows[0])

        errors = WorkbookValidator.validate_rows(rows)

        print(f"Validation Errors : {len(errors)}")

        if errors:
            print(errors)
            raise Exception("\n".join(errors))

        population = self.reader.get_population()

        print(f"Population Records : {len(population)}")

        try:

            print("\nCreating Campaign...")
            self.create_campaign()
            print("Campaign ID :", self.campaign.id)

            print("\nImporting Panchayaths...")
            self.import_panchayaths(rows, population)
            print("Panchayaths Imported :", len(self.panchayaths))

            print("\nImporting Squads...")
            self.import_squads(rows)
            print("Squads Imported :", len(self.squads))

            print("\nImporting Members...")
            self.import_members(rows)

            print("Members Added")

            print("\nCreating Import History...")
            self.create_import_history()

            print("\nCommitting Transaction...")
            db.session.commit()

            print("\nIMPORT COMPLETED SUCCESSFULLY")

        except Exception as ex:

            db.session.rollback()

            print("\nIMPORT FAILED")
            print(type(ex).__name__)
            print(ex)

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

        print("Unique Panchayaths :", len(unique_names))

        if unique_names:
            print("First Five :", unique_names[:5])

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

        count = 0

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

            count += 1

        print("Members Imported :", count)

    ##############################################################

    def create_import_history(self):

        history = ImportHistory(
            campaign_id=self.campaign.id,
            filename=self.filepath.split("\\")[-1],
            status="SUCCESS",
        )

        db.session.add(history)