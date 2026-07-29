from dataclasses import dataclass, field
from typing import Any

from openpyxl import load_workbook


EXPECTED_SHEET = "Pashudhan ID wise Achievement"
REQUIRED_COLUMNS = [
    "PANCHAYATH",
    "SQUAD No.",
    "SQUAD DAYS",
    "SQUAD",
    "Pashudhan ID",
]


@dataclass
class ValidationResult:
    success: bool = False
    message: str = ""
    headers: list[str] = field(default_factory=list)
    rows: int = 0
    errors: list[str] = field(default_factory=list)
    preview: list[list[Any]] = field(default_factory=list)
    column_indexes: dict[str, int] = field(default_factory=dict)


def _normalize_header(value: Any) -> str:
    return str(value).replace("\n", " ").strip()


def _clean_cell(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def validate_excel(filepath):
    result = ValidationResult()

    try:
        workbook = load_workbook(filepath, data_only=True)

        if EXPECTED_SHEET not in workbook.sheetnames:
            result.errors.append(f"Sheet '{EXPECTED_SHEET}' not found.")
            return result

        sheet = workbook[EXPECTED_SHEET]

        raw_headers = [_normalize_header(cell.value) for cell in sheet[1]]
        valid_indexes = [i for i, h in enumerate(raw_headers) if h not in ("", "None")]
        headers = [raw_headers[i] for i in valid_indexes]
        result.headers = headers

        missing = [column for column in REQUIRED_COLUMNS if column not in headers]
        if missing:
            result.errors.append(f"Missing columns: {', '.join(missing)}")
            return result

        result.column_indexes = {
            column: headers.index(column)
            for column in REQUIRED_COLUMNS
        }

        for row in sheet.iter_rows(min_row=2, values_only=True):
            filtered_row = [row[i] if i < len(row) else None for i in valid_indexes]
            if all(v in (None, "") for v in filtered_row):
                continue

            result.rows += 1
            if len(result.preview) < 20:
                result.preview.append([_clean_cell(v) for v in filtered_row])

        result.success = True
        result.message = "Validation completed successfully."
        return result

    except Exception as ex:
        result.errors.append(str(ex))
        return result
