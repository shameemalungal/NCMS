class WorkbookValidator:

    @staticmethod
    def validate_rows(rows):

        errors = []

        for index, row in enumerate(rows, start=2):

            if not row["panchayath"]:
                errors.append(
                    f"Row {index}: Panchayath missing."
                )

            if row["squad_no"] is None:
                errors.append(
                    f"Row {index}: Squad Number missing."
                )

            if not row["member"]:
                errors.append(
                    f"Row {index}: Member missing."
                )

        return errors