from sqlalchemy.orm import Session

from backend.app.models.bank_statement import BankStatementRow


class BankStatementReviewService:
    def __init__(self, db: Session):
        self.db = db

    def get_rows_by_batch(
        self,
        import_batch: str,
        confirmed_only: bool = False,
        unconfirmed_only: bool = False,
        active_only: bool = False,
    ) -> list[BankStatementRow]:
        query = (
            self.db.query(BankStatementRow)
            .filter(BankStatementRow.import_batch == import_batch)
        )

        if confirmed_only:
            query = query.filter(BankStatementRow.is_confirmed == "yes")

        if unconfirmed_only:
            query = query.filter(BankStatementRow.is_confirmed != "yes")

        if active_only:
            query = query.filter(BankStatementRow.is_deleted != "yes")

        return query.order_by(BankStatementRow.id.asc()).all()

    def update_row(
        self,
        row_id: int,
        article: str | None = None,
        project: str | None = None,
        is_confirmed: str | None = None,
        is_deleted: str | None = None,
    ) -> BankStatementRow | None:
        row = (
            self.db.query(BankStatementRow)
            .filter(BankStatementRow.id == row_id)
            .first()
        )

        if not row:
            return None

        if article is not None:
            row.article = article

        if project is not None:
            row.project = project

        if is_confirmed is not None:
            row.is_confirmed = is_confirmed

        if is_deleted is not None:
            row.is_deleted = is_deleted

        self.db.commit()
        self.db.refresh(row)
        return row

    def confirm_rows(self, row_ids: list[int]) -> int:
        rows = (
            self.db.query(BankStatementRow)
            .filter(BankStatementRow.id.in_(row_ids))
            .all()
        )

        updated = 0
        for row in rows:
            if row.is_deleted == "yes":
                continue
            row.is_confirmed = "yes"
            updated += 1

        self.db.commit()
        return updated

    def get_batch_summary(self, import_batch: str) -> dict:
        rows = (
            self.db.query(BankStatementRow)
            .filter(BankStatementRow.import_batch == import_batch)
            .all()
        )

        total_rows = len(rows)
        confirmed_rows = sum(1 for row in rows if row.is_confirmed == "yes")
        deleted_rows = sum(1 for row in rows if row.is_deleted == "yes")
        valid_rows = sum(1 for row in rows if row.validation_status == "valid")
        invalid_rows = sum(1 for row in rows if row.validation_status != "valid")

        return {
            "import_batch": import_batch,
            "total_rows": total_rows,
            "confirmed_rows": confirmed_rows,
            "deleted_rows": deleted_rows,
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
        }