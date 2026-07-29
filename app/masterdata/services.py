from openpyxl import load_workbook


REQUIRED_COLUMNS = [
    "PANCHAYATH",
    "SQUAD No.",
    "SQUAD DAYS",
    "SQUAD",
    "Pashudhan ID",
]


class ValidationResult:

    def __init__(self):

        self.success = False

        self.message = ""

        self.headers = []

        self.rows = 0

        self.errors = []

        self.preview = []


def validate_excel(filepath):

    result = ValidationResult()

    try:

        workbook = load_workbook(
            filepath,
            data_only=True,
        )

        sheet = workbook["Pashudhan ID wise Achievement"]

        ####################################################
        # Read first row
        ####################################################

        raw_headers = [
            cell.value
            for cell in sheet[1]
        ]

        ####################################################
        # Keep only non-empty columns
        ####################################################

        valid_indexes = [
            i
            for i, h in enumerate(raw_headers)
            if h not in (None, "")
        ]

        headers = [
            str(raw_headers[i]).strip()
            for i in valid_indexes
        ]

        result.headers = headers

        ####################################################
        # Validate required columns
        ####################################################

        missing = [
            column
            for column in REQUIRED_COLUMNS
            if column not in headers
        ]

        if missing:

            result.errors.append(
                f"Missing columns: {', '.join(missing)}"
            )

            return result

        ####################################################
        # Read preview
        ####################################################

        for row in sheet.iter_rows(
            min_row=2,
            values_only=True,
        ):

            filtered_row = [
                row[i]
                if i < len(row)
                else ""
                for i in valid_indexes
            ]

            if all(
                v in (None, "")
                for v in filtered_row
            ):
                continue

            result.rows += 1

            if len(result.preview) < 20:

                result.preview.append([
                    "" if v is None else v
                    for v in filtered_row
                ])

        result.success = True
        result.message = "Validation completed successfully."

        return result

    except Exception as ex:

        result.errors.append(str(ex))

        return result