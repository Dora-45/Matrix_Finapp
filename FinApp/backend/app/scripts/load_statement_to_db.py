from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.db.base import Base
from backend.app.db.session import SessionLocal, engine
from backend.app.models.bank_statement import BankStatementRow
import backend.app.models
from backend.app.repositories.bank_statement_repository import BankStatementRepository
from backend.app.services.bank_statement_validation_service import (
    BankStatementValidationService,
)
from backend.app.services.sber_statement_parser import parse_sber_statement


def build_import_batch(file_path: str) -> str:
    filename = Path(file_path).stem
    return f"{filename}_{uuid4().hex[:8]}"


def prepare_rows(raw_rows: list[dict], import_batch: str) -> list[dict]:
    prepared = []

    for index, row in enumerate(raw_rows, start=1):
        prepared.append(
            {
                "import_batch": import_batch,
                "source_file": row.get("source_file"),
                "source_sheet": row.get("source_sheet"),
                "row_number": index,
                "operation_datetime": row.get("operation_datetime"),
                "account_number": row.get("account_number"),
                "account_type": row.get("account_type"),
                "direction": row.get("direction"),
                "amount": row.get("amount"),
                "currency": row.get("currency", "RUB"),
                "counterparty_account": row.get("counterparty_account"),
                "counterparty_name": row.get("counterparty_name"),
                "bank_name": row.get("bank_name"),
                "document_number": row.get("document_number"),
                "operation_code": row.get("operation_code"),
                "payment_purpose": row.get("payment_purpose"),
                "article": row.get("article"),
                "project": row.get("project"),
                "validation_status": "new",
                "validation_message": None,
                "is_confirmed": "no",
                "is_deleted": "no",
            }
        )

    return prepared


def print_summary(rows: list[BankStatementRow], import_batch: str) -> None:
    total = len(rows)
    valid = sum(1 for row in rows if row.validation_status == "valid")
    warning = sum(1 for row in rows if row.validation_status == "warning")
    error = sum(1 for row in rows if row.validation_status == "error")

    print("\n=== IMPORT RESULT ===")
    print(f"import_batch: {import_batch}")
    print(f"total_rows: {total}")
    print(f"valid: {valid}")
    print(f"warning: {warning}")
    print(f"error: {error}")

    print("\n=== FIRST 10 ROWS ===")
    for row in rows[:10]:
        print(
            f"[id={row.id}] "
            f"{row.operation_datetime} | "
            f"{row.direction} | "
            f"{row.amount} | "
            f"{row.counterparty_name} | "
            f"{row.validation_status} | "
            f"{row.validation_message}"
        )


def main(file_path: str) -> None:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    Base.metadata.create_all(bind=engine)

    raw_rows = parse_sber_statement(str(path))
    if not raw_rows:
        raise ValueError("Не удалось найти операции в выписке")

    import_batch = build_import_batch(str(path))
    prepared_rows = prepare_rows(raw_rows, import_batch)

    db: Session = SessionLocal()
    try:
        repo = BankStatementRepository(db)
        inserted_rows = repo.create_many(prepared_rows)

        validator = BankStatementValidationService()
        validator.validate_rows(inserted_rows)

        db.commit()
        for row in inserted_rows:
            db.refresh(row)

        print_summary(inserted_rows, import_batch)

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("python -m backend.app.scripts.load_statement_to_db <путь_к_файлу>")
        sys.exit(1)

    main(sys.argv[1])