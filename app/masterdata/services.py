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

        headers = []

        for cell in sheet[1]:
            if cell.value:
                headers.append(str(cell.value).strip())
            else:
                headers.append("")

        result.headers = headers

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

        for row in sheet.iter_rows(
            min_row=2,
            values_only=True,
        ):

            if all(v is None for v in row):
                continue

            result.rows += 1

            if len(result.preview) < 20:
                result.preview.append(row[:len(result.headers)])

        result.success = True

        result.message = "Validation completed successfully."

        return result

    except Exception as ex:

        result.errors.append(str(ex))

        return result