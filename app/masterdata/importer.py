import re
import secrets

from app.extensions import db
from app.models import Campaign, Panchayath, Squad, SquadMember, ImportHistory


class MasterDataImporter:
    def __init__(self, file_path, campaign_id):
        self.file_path = file_path
        self.campaign_id = campaign_id
        self.summary = {
            "campaign_created": False,
            "panchayaths_created": 0,
            "panchayaths_updated": 0,
            "squads_created": 0,
            "squads_updated": 0,
            "members_created": 0,
            "errors": [],
        }

    def _get_or_create_campaign(self):
        campaign = Campaign.query.get(self.campaign_id)
        if campaign is None:
            raise Exception("Selected campaign not found.")
        return campaign

    def import_data(self):
        try:
            campaign = self._get_or_create_campaign()

            from openpyxl import load_workbook

            workbook = load_workbook(self.file_path, data_only=True)
            sheet = workbook["Pashudhan ID wise Achievement"]
            population_sheet = workbook["Panchayath Population"] if "Panchayath Population" in workbook.sheetnames else None

            population_map = {}
            if population_sheet is not None:
                for row in population_sheet.iter_rows(min_row=2, values_only=True):
                    panchayath_name = row[0] if len(row) > 0 else None
                    population = row[1] if len(row) > 1 else 0
                    if not panchayath_name:
                        continue
                    name = str(panchayath_name).strip()
                    if not name or name.lower() == "nan" or "total" in name.lower():
                        continue
                    population_map[name] = int(population or 0)

            headers = [str(c.value).strip() if c.value is not None else "" for c in sheet[1]]
            header_index = {h: i for i, h in enumerate(headers) if h}

            panchayath_cache = {}

            for row in sheet.iter_rows(min_row=2, values_only=True):
                if all(v in (None, "") for v in row):
                    continue

                name = str(row[header_index["PANCHAYATH"]]).strip()
                if not name or name.lower() == "nan" or "total" in name.lower():
                    continue

                squad_no = int(row[header_index["SQUAD No."]])
                squad_days = int(row[header_index["SQUAD DAYS"]] or 0)
                member_text = str(row[header_index["SQUAD"]]).strip()
                pashudhan_id = str(row[header_index["Pashudhan ID"]]).strip()
                population = population_map.get(name, 0)

                panchayath = panchayath_cache.get(name)
                if panchayath is None:
                    panchayath = Panchayath.query.filter_by(campaign_id=campaign.id, name=name).first()
                    if panchayath is None:
                        panchayath = Panchayath(campaign_id=campaign.id, name=name, population=population)
                        db.session.add(panchayath)
                        db.session.flush()
                        self.summary["panchayaths_created"] += 1
                    else:
                        panchayath.population = population
                        self.summary["panchayaths_updated"] += 1
                    panchayath_cache[name] = panchayath

                squad = Squad.query.filter_by(campaign_id=campaign.id, squad_no=squad_no).first()
                if squad is None:
                    squad = Squad(
                        campaign_id=campaign.id,
                        panchayath_id=panchayath.id,
                        squad_no=squad_no,
                        squad_days=squad_days,
                        target=population,
                        submission_token=secrets.token_hex(16),
                        status="Pending",
                    )
                    db.session.add(squad)
                    db.session.flush()
                    self.summary["squads_created"] += 1
                else:
                    squad.panchayath_id = panchayath.id
                    squad.squad_days = squad_days
                    squad.target = population
                    self.summary["squads_updated"] += 1

                member_name = member_text
                office = ""
                match = re.match(r"^(.*?)\s*\((.*?)\)$", member_text)
                if match:
                    member_name = match.group(1).strip()
                    office = match.group(2).strip()

                existing_member = SquadMember.query.filter_by(squad_id=squad.id, pashudhan_id=pashudhan_id).first()
                if existing_member is None:
                    db.session.add(
                        SquadMember(
                            squad_id=squad.id,
                            member_name=member_name,
                            office=office,
                            pashudhan_id=pashudhan_id,
                            full_text=member_text,
                        )
                    )
                    self.summary["members_created"] += 1
                else:
                    existing_member.member_name = member_name
                    existing_member.office = office
                    existing_member.full_text = member_text

            db.session.add(
                ImportHistory(
                    campaign_id=campaign.id,
                    filename=self.file_path.split("/")[-1].split("\\")[-1],
                    status="SUCCESS",
                )
            )
            db.session.commit()
            return self.summary
        except Exception as e:
            db.session.rollback()
            self.summary["errors"].append(str(e))
            return self.summary
