from sqlalchemy.orm import Session

from backend.app.models.bank_statement import BankStatementRow


class BankStatementRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_many(self, rows: list[dict]) -> list[BankStatementRow]:
        objects = [BankStatementRow(**row) for row in rows]
        self.db.add_all(objects)
        self.db.commit()
        for obj in objects:
            self.db.refresh(obj)
        return objects

    def list_batch(self, import_batch: str) -> list[BankStatementRow]:
        return (
            self.db.query(BankStatementRow)
            .filter(BankStatementRow.import_batch == import_batch)
            .filter(BankStatementRow.is_deleted != "yes")
            .order_by(BankStatementRow.id.asc())
            .all()
        )

    def get_by_id(self, row_id: int) -> BankStatementRow | None:
        return self.db.query(BankStatementRow).filter(BankStatementRow.id == row_id).first()

    def mark_confirmed(self, row_id: int) -> BankStatementRow | None:
        row = self.get_by_id(row_id)
        if not row:
            return None
        row.is_confirmed = "yes"
        self.db.commit()
        self.db.refresh(row)
        return row

    def mark_deleted(self, row_id: int) -> BankStatementRow | None:
        row = self.get_by_id(row_id)
        if not row:
            return None
        row.is_deleted = "yes"
        self.db.commit()
        self.db.refresh(row)
        return row