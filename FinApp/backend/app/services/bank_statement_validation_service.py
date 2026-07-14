from backend.app.models.bank_statement import BankStatementRow


class BankStatementValidationService:
    def validate_row(self, row: BankStatementRow) -> tuple[str, str | None]:
        if row.is_deleted == "yes":
            return "warning", "Строка помечена как удаленная"

        if not row.operation_datetime:
            return "error", "Не заполнена дата операции"

        if not row.direction or row.direction not in ("inflow", "outflow"):
            return "error", "Не определено направление операции"

        if row.amount is None:
            return "error", "Не указана сумма"

        if float(row.amount) <= 0:
            return "error", "Сумма должна быть больше нуля"

        if not row.payment_purpose or not row.payment_purpose.strip():
            return "warning", "Пустое назначение платежа"

        if not row.account_type:
            return "warning", "Не определен тип счета"

        return "valid", None

    def validate_rows(self, rows: list[BankStatementRow]) -> None:
        for row in rows:
            status, message = self.validate_row(row)
            row.validation_status = status
            row.validation_message = message