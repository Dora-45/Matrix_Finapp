from __future__ import annotations

import sys

from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.models.bank_statement import BankStatementRow
from backend.app.services.bank_statement_validation_service import (
    BankStatementValidationService,
)


ALLOWED_FIELDS = {
    "operation_datetime",
    "account_number",
    "account_type",
    "direction",
    "amount",
    "currency",
    "counterparty_account",
    "counterparty_name",
    "bank_name",
    "document_number",
    "operation_code",
    "payment_purpose",
    "article",
    "project",
    "is_confirmed",
    "is_deleted",
}


def print_row(row: BankStatementRow) -> None:
    print("\n=== UPDATED ROW ===")
    print(f"id: {row.id}")
    print(f"operation_datetime: {row.operation_datetime}")
    print(f"account_number: {row.account_number}")
    print(f"account_type: {row.account_type}")
    print(f"direction: {row.direction}")
    print(f"amount: {row.amount}")
    print(f"currency: {row.currency}")
    print(f"counterparty_account: {row.counterparty_account}")
    print(f"counterparty_name: {row.counterparty_name}")
    print(f"bank_name: {row.bank_name}")
    print(f"document_number: {row.document_number}")
    print(f"operation_code: {row.operation_code}")
    print(f"payment_purpose: {row.payment_purpose}")
    print(f"article: {row.article}")
    print(f"project: {row.project}")
    print(f"validation_status: {row.validation_status}")
    print(f"validation_message: {row.validation_message}")
    print(f"is_confirmed: {row.is_confirmed}")
    print(f"is_deleted: {row.is_deleted}")


def cast_value(field: str, value: str):
    if field == "amount":
        return float(value)
    return value


def main() -> None:
    if len(sys.argv) < 4:
        print("Использование:")
        print("python -m backend.app.scripts.update_statement_row <row_id> <field> <value>")
        print("")
        print("Примеры:")
        print('python -m backend.app.scripts.update_statement_row 11 article "Маркетинг и реклама"')
        print('python -m backend.app.scripts.update_statement_row 18 article "Заработная плата"')
        print('python -m backend.app.scripts.update_statement_row 18 is_confirmed yes')
        sys.exit(1)

    row_id = int(sys.argv[1])
    field = sys.argv[2]
    value = " ".join(sys.argv[3:])

    if field not in ALLOWED_FIELDS:
        print(f"Поле '{field}' нельзя редактировать через этот скрипт.")
        print(f"Разрешённые поля: {', '.join(sorted(ALLOWED_FIELDS))}")
        sys.exit(1)

    db: Session = SessionLocal()
    try:
        row = db.query(BankStatementRow).filter(BankStatementRow.id == row_id).first()
        if not row:
            print(f"Строка с id={row_id} не найдена.")
            sys.exit(1)

        setattr(row, field, cast_value(field, value))

        validator = BankStatementValidationService()
        status, message = validator.validate_row(row)
        row.validation_status = status
        row.validation_message = message

        db.commit()
        db.refresh(row)

        print_row(row)

    finally:
        db.close()


if __name__ == "__main__":
    main()