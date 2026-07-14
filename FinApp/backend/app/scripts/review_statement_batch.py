from __future__ import annotations

import sys

from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.models.bank_statement import BankStatementRow


def format_cell(value, max_len: int = 40) -> str:
    if value is None:
        return ""
    text = str(value).replace("\n", " ").replace("\r", " ").strip()
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def print_rows(rows: list[BankStatementRow]) -> None:
    print("\n=== BATCH ROWS ===")
    for row in rows:
        print(
            f"id={row.id} | "
            f"dt={row.operation_datetime} | "
            f"dir={row.direction} | "
            f"amount={row.amount} | "
            f"account_type={row.account_type} | "
            f"counterparty={format_cell(row.counterparty_name, 30)} | "
            f"purpose={format_cell(row.payment_purpose, 60)} | "
            f"status={row.validation_status} | "
            f"confirmed={row.is_confirmed} | "
            f"deleted={row.is_deleted}"
        )


def print_summary(rows: list[BankStatementRow], import_batch: str) -> None:
    total = len(rows)
    valid = sum(1 for row in rows if row.validation_status == "valid")
    warning = sum(1 for row in rows if row.validation_status == "warning")
    error = sum(1 for row in rows if row.validation_status == "error")
    confirmed = sum(1 for row in rows if row.is_confirmed == "yes")
    deleted = sum(1 for row in rows if row.is_deleted == "yes")

    print("\n=== BATCH SUMMARY ===")
    print(f"import_batch: {import_batch}")
    print(f"total: {total}")
    print(f"valid: {valid}")
    print(f"warning: {warning}")
    print(f"error: {error}")
    print(f"confirmed: {confirmed}")
    print(f"deleted: {deleted}")


def load_rows(
    db: Session,
    import_batch: str,
    only_issues: bool = False,
    limit: int | None = None,
) -> list[BankStatementRow]:
    query = (
        db.query(BankStatementRow)
        .filter(BankStatementRow.import_batch == import_batch)
        .order_by(BankStatementRow.id.asc())
    )

    if only_issues:
        query = query.filter(BankStatementRow.validation_status.in_(["warning", "error"]))

    if limit is not None:
        query = query.limit(limit)

    return query.all()


def main() -> None:
    if len(sys.argv) < 2:
        print("Использование:")
        print("python -m backend.app.scripts.review_statement_batch <import_batch> [issues] [limit]")
        print("")
        print("Примеры:")
        print('python -m backend.app.scripts.review_statement_batch "my_batch_123"')
        print('python -m backend.app.scripts.review_statement_batch "my_batch_123" issues')
        print('python -m backend.app.scripts.review_statement_batch "my_batch_123" issues 20')
        sys.exit(1)

    import_batch = sys.argv[1]
    only_issues = len(sys.argv) >= 3 and sys.argv[2].lower() == "issues"

    limit = None
    if len(sys.argv) >= 4:
        limit = int(sys.argv[3])

    db: Session = SessionLocal()
    try:
        rows = load_rows(db, import_batch, only_issues=only_issues, limit=limit)

        if not rows:
            print("Строки не найдены.")
            return

        print_summary(rows, import_batch)
        print_rows(rows)

    finally:
        db.close()


if __name__ == "__main__":
    main()