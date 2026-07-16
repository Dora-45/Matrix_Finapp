from sqlalchemy.orm import Session

from backend.app.models.cashflow_operation import CashflowOperation
from backend.app.models.pnl_category import PnlCategory
from backend.app.repositories.pnl_category_repository import PnlCategoryRepository


class PnlClassificationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PnlCategoryRepository(db)

    def classify_all(self) -> int:
        self.repo.seed_defaults()

        operations = self.db.query(CashflowOperation).all()
        categories = self.repo.get_all_active()

        updated_count = 0

        for op in operations:
            matched = self._find_category(op, categories)

            if matched is None:
                if (
                    op.pnl_group is not None
                    or op.pnl_article is not None
                    or op.pnl_sign is not None
                ):
                    op.pnl_group = None
                    op.pnl_article = None
                    op.pnl_sign = None
                    updated_count += 1
                continue

            changed = False

            if op.pnl_group != matched.pnl_group:
                op.pnl_group = matched.pnl_group
                changed = True

            if op.pnl_article != matched.pnl_article:
                op.pnl_article = matched.pnl_article
                changed = True

            if op.pnl_sign != matched.pnl_sign:
                op.pnl_sign = matched.pnl_sign
                changed = True

            if changed:
                updated_count += 1

        self.db.commit()
        return updated_count

    def _find_category(
        self,
        op: CashflowOperation,
        categories: list[PnlCategory],
    ) -> PnlCategory | None:
        purpose = (op.payment_purpose or "").lower()
        counterparty = (op.counterparty_name or "").lower()
        haystack = f"{purpose} {counterparty}".strip()

        for category in categories:
            if category.direction != op.direction:
                continue

            if not self._account_type_matches(op.account_type, category.account_type_filter):
                continue

            keywords = self._split_keywords(category.keywords)
            if not keywords:
                continue

            if any(keyword in haystack for keyword in keywords):
                return category

        return self._fallback_category(op)

    def _account_type_matches(self, account_type: str | None, account_type_filter: str) -> bool:
        if account_type_filter == "all":
            return True
        return (account_type or "").lower() == account_type_filter.lower()

    def _split_keywords(self, raw_keywords: str | None) -> list[str]:
        if not raw_keywords:
            return []
        return [item.strip().lower() for item in raw_keywords.split(",") if item.strip()]

    def _fallback_category(self, op: CashflowOperation) -> PnlCategory | None:
        if op.direction == "inflow":
            return PnlCategory(
                direction="inflow",
                pnl_sign="income",
                pnl_group="other_income",
                pnl_article="Прочие доходы",
                keywords="",
                account_type_filter="all",
                priority=0,
                is_active=True,
            )

        if op.direction == "outflow":
            return PnlCategory(
                direction="outflow",
                pnl_sign="expense",
                pnl_group="operating_expenses",
                pnl_article="Прочие операционные расходы",
                keywords="",
                account_type_filter="all",
                priority=0,
                is_active=True,
            )

        return None