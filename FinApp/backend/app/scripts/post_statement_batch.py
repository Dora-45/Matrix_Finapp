from __future__ import annotations

import sys

from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.services.bank_statement_posting_service import (
    BankStatementPostingService,
)


def main() -> None:
    if len(sys.argv) < 2:
        print("Использование:")
        print("python -m backend.app.scripts.post_statement_batch <import_batch>")
        print("")
        print("Пример:")
        print('python -m backend.app.scripts.post_statement_batch "my_batch_123"')
        sys.exit(1)

    import_batch = sys.argv[1]

    db: Session = SessionLocal()
    try:
        service = BankStatementPostingService(db)
        result = service.post_confirmed_rows(import_batch)

        print("\n=== POSTING RESULT ===")
        print(f"import_batch: {result['import_batch']}")
        print(f"posted_rows: {result['posted_rows']}")

    finally:
        db.close()


if __name__ == "__main__":
    main()