from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.models.bank_statement import BankStatementRow
from backend.app.repositories.cashflow_category_repository import CashflowCategoryRepository


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
        account_type: str | None = None,
        amount: Decimal | None = None,
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

        if account_type is not None:
            row.account_type = account_type

        if amount is not None:
            row.amount = amount

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

    def get_all_batches(self) -> list[dict]:
        """
        Возвращает список всех партий импорта (историю выписок) с краткой сводкой.
        Старые выписки никогда не удаляются из базы при загрузке новой — у каждой
        загрузки свой уникальный import_batch, этот метод делает историю видимой.
        """
        rows = self.db.query(BankStatementRow).all()

        batches: dict[str, dict] = {}
        for row in rows:
            key = row.import_batch
            if key not in batches:
                batches[key] = {
                    "import_batch": key,
                    "source_file": row.source_file,
                    "total_rows": 0,
                    "confirmed_rows": 0,
                    "deleted_rows": 0,
                    "min_date": None,
                    "max_date": None,
                }

            b = batches[key]
            b["total_rows"] += 1
            if row.is_confirmed == "yes":
                b["confirmed_rows"] += 1
            if row.is_deleted == "yes":
                b["deleted_rows"] += 1

            if row.operation_datetime:
                if b["min_date"] is None or row.operation_datetime < b["min_date"]:
                    b["min_date"] = row.operation_datetime
                if b["max_date"] is None or row.operation_datetime > b["max_date"]:
                    b["max_date"] = row.operation_datetime

        result = list(batches.values())
        result.sort(key=lambda b: b["max_date"] or "", reverse=True)
        return result

    def auto_classify_batch(self, import_batch: str) -> dict:
        """
        Автоматически подставляет статью (article) и раздел ДДС (project)
        для строк батча без статьи, используя ключевые слова из справочника
        CashflowCategory. Не трогает строки с уже заполненной статьёй и не
        трогает account_type — тип счёта (расчётный/кредитный/личный)
        редактируется отдельно вручную, так как в выписке он не всегда
        определяется однозначно (например, кредитная карта может быть
        привязана к расчётному счёту в проводке).
        """
        category_repo = CashflowCategoryRepository(self.db)
        categories = category_repo.get_all_active()

        rows = (
            self.db.query(BankStatementRow)
            .filter(BankStatementRow.import_batch == import_batch)
            .filter(BankStatementRow.is_deleted != "yes")
            .filter((BankStatementRow.article.is_(None)) | (BankStatementRow.article == ""))
            .all()
        )

        classified = 0
        fallbacked = 0

        for row in rows:
            purpose = (row.payment_purpose or "").lower()
            counterparty = (row.counterparty_name or "").lower()
            search_text = f"{purpose} {counterparty}"

            matched = None
            for cat in categories:
                if cat.account_type_filter != "all" and row.account_type != cat.account_type_filter:
                    continue
                if cat.direction != row.direction:
                    continue
                keywords = [kw.strip().lower() for kw in cat.keywords.split(",") if kw.strip()]
                if any(keyword in search_text for keyword in keywords):
                    matched = cat
                    break

            if matched:
                row.article = matched.article
                row.project = matched.section
                classified += 1
            else:
                row.article = "Прочие поступления" if row.direction == "inflow" else "Прочие расходы"
                row.project = "operating"
                fallbacked += 1

        self.db.commit()
        return {"classified": classified, "fallbacked": fallbacked, "total": len(rows)}