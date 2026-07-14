from __future__ import annotations

import sys

from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.models.bank_statement import BankStatementRow


def main() -> None:
    if len(sys.argv) < 2:
        print("Использование:")
        print("python -m backend.app.scripts.confirm_statement_rows <row_id_1> <row_id_2> ...")
        print("")
        print("Пример:")
        print("python -m backend.app.scripts.confirm_statement_rows 11 17 18")
        sys.exit(1)

    try:
        row_ids = [int(value) for value in sys.argv[1:]]
    except ValueError:
        print("Все id должны быть целыми числами.")
        sys.exit(1)

    db: Session = SessionLocal()
    try:
        rows = (
            db.query(BankStatementRow)
            .filter(BankStatementRow.id.in_(row_ids))
            .order_by(BankStatementRow.id.asc())
            .all()
        )

        if not rows:
            print("Строки не найдены.")
            sys.exit(1)

        found_ids = {row.id for row in rows}
        missing_ids = [row_id for row_id in row_ids if row_id not in found_ids]

        updated = 0
        skipped_deleted = 0

        for row in rows:
            if row.is_deleted == "yes":
                skipped_deleted += 1
                continue

            row.is_confirmed = "yes"
            updated += 1

        db.commit()

        print("\n=== CONFIRM RESULT ===")
        print(f"requested_ids: {row_ids}")
        print(f"updated: {updated}")
        print(f"skipped_deleted: {skipped_deleted}")
        print(f"missing_ids: {missing_ids}")

        print("\n=== CONFIRMED ROWS ===")
        for row in rows:
            db.refresh(row)
            print(
                f"id={row.id} | "
                f"amount={row.amount} | "
                f"direction={row.direction} | "
                f"article={row.article} | "
                f"is_confirmed={row.is_confirmed} | "
                f"is_deleted={row.is_deleted}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()