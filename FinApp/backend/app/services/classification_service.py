from sqlalchemy.orm import Session

from backend.app.models.cashflow_operation import CashflowOperation
from backend.app.repositories.cashflow_category_repository import CashflowCategoryRepository


class ClassificationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CashflowCategoryRepository(db)

    def classify_all_unclassified(self) -> dict:
        categories = self.repo.get_all_active()
        operations = (
            self.db.query(CashflowOperation)
            .filter(CashflowOperation.article == None)
            .all()
        )

        classified = 0
        fallbacked = 0

        for op in operations:
            matched = self._find_category(op, categories)
            if matched:
                op.article = matched.article
                op.section = matched.section
                classified += 1
            else:
                op.article = "Прочие поступления" if op.direction == "inflow" else "Прочие расходы"
                op.section = "operating"
                fallbacked += 1

        self.db.commit()
        return {
            "classified": classified,
            "unclassified": fallbacked,
        }

    def reclassify_all(self) -> dict:
        operations = self.db.query(CashflowOperation).all()
        categories = self.repo.get_all_active()

        matched_count = 0
        fallbacked = 0

        for op in operations:
            matched = self._find_category(op, categories)
            if matched:
                op.article = matched.article
                op.section = matched.section
                matched_count += 1
            else:
                op.article = "Прочие поступления" if op.direction == "inflow" else "Прочие расходы"
                op.section = "operating"
                fallbacked += 1

        self.db.commit()
        return {
            "reclassified": matched_count,
            "fallbacked": fallbacked,
            "total": len(operations),
        }

    def _find_category(self, op: CashflowOperation, categories):
        purpose = (op.payment_purpose or "").lower()
        counterparty = (op.counterparty_name or "").lower()
        search_text = f"{purpose} {counterparty}"

        for cat in categories:
            if cat.account_type_filter != "all" and op.account_type != cat.account_type_filter:
                continue

            if cat.direction != op.direction:
                continue

            keywords = [kw.strip().lower() for kw in cat.keywords.split(",") if kw.strip()]
            if any(keyword in search_text for keyword in keywords):
                return cat

        return None
