from sqlalchemy.orm import Session

from backend.app.models.bank_statement import BankStatementRow
from backend.app.models.cashflow_operation import CashflowOperation


class BankStatementPostingService:
    def __init__(self, db: Session):
        self.db = db

    def post_confirmed_rows(self, import_batch: str) -> dict:
        rows = (
            self.db.query(BankStatementRow)
            .filter(BankStatementRow.import_batch == import_batch)
            .filter(BankStatementRow.is_deleted != "yes")
            .filter(BankStatementRow.is_confirmed == "yes")
            .all()
        )

        inserted = 0
        skipped_duplicates = 0

        for row in rows:
            exists = (
                self.db.query(CashflowOperation)
                .filter(CashflowOperation.source_file == row.source_file)
                .filter(CashflowOperation.source_sheet == row.source_sheet)
                .filter(CashflowOperation.operation_datetime == row.operation_datetime)
                .filter(CashflowOperation.amount == row.amount)
                .filter(CashflowOperation.direction == row.direction)
                .first()
            )

            if exists:
                skipped_duplicates += 1
                continue

            operation = CashflowOperation(
                operation_datetime=row.operation_datetime,
                account_number=row.account_number or "unknown",
                account_type=row.account_type or "checking",
                direction=row.direction or "outflow",
                amount=row.amount,
                currency=row.currency or "RUB",
                counterparty_name=row.counterparty_name,
                payment_purpose=row.payment_purpose or "",
                source_file=row.source_file or "unknown",
                source_sheet=row.source_sheet or "unknown",
                article=row.article,
                # project в BankStatementRow хранил секцию — переносим в section
                section=row.project,
                project=None,
                is_manual="no",
            )

            self.db.add(operation)
            inserted += 1

        self.db.commit()

        return {
            "import_batch": import_batch,
            "posted_rows": inserted,
            "skipped_duplicates": skipped_duplicates,
        }
