from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.models.cashflow_operation import CashflowOperation


def format_cell(value, max_len: int = 50) -> str:
    if value is None:
        return ""
    text = str(value).replace("\n", " ").replace("\r", " ").strip()
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def main() -> None:
    db: Session = SessionLocal()
    try:
        rows = (
            db.query(CashflowOperation)
            .order_by(CashflowOperation.id.asc())
            .all()
        )

        print("\n=== CASHFLOW OPERATIONS ===")
        print(f"total: {len(rows)}")

        for row in rows:
            print(
                f"id={row.id} | "
                f"dt={row.operation_datetime} | "
                f"dir={row.direction} | "
                f"amount={row.amount} | "
                f"account_type={row.account_type} | "
                f"article={format_cell(row.article, 30)} | "
                f"purpose={format_cell(row.payment_purpose, 60)} | "
                f"source_file={format_cell(row.source_file, 35)} | "
                f"source_sheet={format_cell(row.source_sheet, 20)}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()