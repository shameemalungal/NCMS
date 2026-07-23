import re
import secrets

import pandas as pd

from app.extensions import db
from app.masterdata.services import MasterDataService


class MasterDataImporter:

    REQUIRED_POP_COLUMNS = [
        "PANCHAYATH",
        "Population FMD"
    ]

    REQUIRED_SQUAD_COLUMNS = [
        "PANCHAYATH",
        "SQUAD No.",
        "SQUAD DAYS",
        "SQUAD",
        "Pashudhan ID"
    ]

    def __init__(self, file_path, campaign_name):

        self.file_path = file_path
        self.campaign_name = campaign_name

        self.summary = {
            "campaign_created": False,
            "panchayaths_created": 0,
            "panchayaths_updated": 0,
            "squads_created": 0,
            "squads_updated": 0,
            "errors": []
        }

    @staticmethod
    def clean_columns(df):
        df.columns = (
            df.columns.astype(str)
            .str.replace("\n", " ", regex=False)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )
        return df

    @staticmethod
    def validate_columns(df, required, sheet_name):

        missing = []

        for col in required:
            if col not in df.columns:
                missing.append(col)

        if missing:
            raise Exception(
                f"{sheet_name}: Missing columns -> {', '.join(missing)}"
            )

    def import_data(self):

        try:

            workbook = pd.ExcelFile(self.file_path)

            if "Panchayath Population" not in workbook.sheet_names:
                raise Exception("Sheet 'Panchayath Population' not found.")

            if "Pashudhan ID wise Achievement" not in workbook.sheet_names:
                raise Exception("Sheet 'Pashudhan ID wise Achievement' not found.")

            pop_df = pd.read_excel(
                workbook,
                sheet_name="Panchayath Population"
            )

            squad_df = pd.read_excel(
                workbook,
                sheet_name="Pashudhan ID wise Achievement"
            )

            pop_df = self.clean_columns(pop_df)
            squad_df = self.clean_columns(squad_df)

            self.validate_columns(
                pop_df,
                self.REQUIRED_POP_COLUMNS,
                "Panchayath Population"
            )

            self.validate_columns(
                squad_df,
                self.REQUIRED_SQUAD_COLUMNS,
                "Pashudhan ID wise Achievement"
            )

            campaign, created = (
                MasterDataService.get_or_create_campaign(
                    self.campaign_name
                )
            )

            self.summary["campaign_created"] = created

            panchayath_cache = {}

            # -------------------------------------------------
            # Import Panchayaths
            # -------------------------------------------------

            for _, row in pop_df.iterrows():

                # Skip blank rows
                if pd.isna(row["PANCHAYATH"]):
                    continue

                name = str(row["PANCHAYATH"]).strip()

                # Skip blank names
                if not name:
                    continue

                # Skip NaN text
                if name.lower() == "nan":
                    continue

                # Skip total/footer rows
                if "total" in name.lower():
                    continue

                population = row["Population FMD"]

                if pd.isna(population):
                    population = 0

                population = int(population)

                panchayath, created = (
                    MasterDataService.get_or_create_panchayath(
                        name=name,
                        population=population
                    )
                )

                panchayath_cache[name] = panchayath

                if created:
                    self.summary["panchayaths_created"] += 1
                else:
                    self.summary["panchayaths_updated"] += 1

            db.session.flush()

            # -------------------------------------------------
            # Import Squads
            # -------------------------------------------------

            for _, row in squad_df.iterrows():

                name = str(row["PANCHAYATH"]).strip()

                if name not in panchayath_cache:
                    raise Exception(
                        f"Panchayath '{name}' not found."
                    )

                member = str(row["SQUAD"]).strip()

                office = ""

                match = re.match(
                    r"^(.*?)\s*\((.*?)\)$",
                    member
                )

                if match:
                    member = match.group(1).strip()
                    office = match.group(2).strip()

                squad, created = (
                    MasterDataService.get_or_create_squad(
                        campaign=campaign,
                        panchayath=panchayath_cache[name],
                        squad_no=int(row["SQUAD No."]),
                        squad_days=int(row["SQUAD DAYS"]),
                        squad_member=member,
                        office=office,
                        pashudhan_id=str(
                            row["Pashudhan ID"]
                        ).strip(),
                        submission_token=secrets.token_hex(24)
                    )
                )

                if created:
                    self.summary["squads_created"] += 1
                else:
                    self.summary["squads_updated"] += 1

            db.session.commit()

            return self.summary

        except Exception as e:

            db.session.rollback()

            self.summary["errors"].append(str(e))

            return self.summary