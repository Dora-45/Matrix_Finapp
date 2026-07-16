from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.models.cashflow_operation import CashflowOperation
from backend.app.schemas.cashflow import PnLReportLine, PnLReportResponse
from backend.app.services.pnl_classification_service import PnlClassificationService


class PnlService:
    def __init__(self, db: Session):
        self.db = db
        self.classifier = PnlClassificationService(db)

    def get_report(self, period_from: str, period_to: str) -> PnLReportResponse:
        self.classifier.classify_all()

        operations = (
            self.db.query(CashflowOperation)
            .filter(CashflowOperation.operation_datetime >= f"{period_from} 00:00:00")
            .filter(CashflowOperation.operation_datetime <= f"{period_to} 23:59:59")
            .all()
        )

        grouped: dict[tuple[str, str, str], Decimal] = {}

        for op in operations:
            if not op.pnl_group or not op.pnl_article or not op.pnl_sign:
                continue

            key = (op.pnl_group, op.pnl_article, op.pnl_sign)
            grouped[key] = grouped.get(key, Decimal("0")) + op.amount

        lines: list[PnLReportLine] = []
        for (pnl_group, pnl_article, pnl_sign), total in sorted(grouped.items()):
            lines.append(
                PnLReportLine(
                    pnl_group=pnl_group,
                    pnl_article=pnl_article,
                    pnl_sign=pnl_sign,
                    total=total,
                )
            )

        revenue = self._sum_group(lines, "revenue")
        cogs = self._sum_group(lines, "cogs")
        operating_expenses = self._sum_group(lines, "operating_expenses")
        other_income = self._sum_group(lines, "other_income")
        other_expenses = self._sum_group(lines, "other_expenses")
        taxes = self._sum_group(lines, "taxes")

        gross_profit = revenue - cogs
        operating_profit = gross_profit - operating_expenses
        net_profit = operating_profit + other_income - other_expenses - taxes

        return PnLReportResponse(
            period_from=period_from,
            period_to=period_to,
            revenue=revenue,
            cogs=cogs,
            gross_profit=gross_profit,
            operating_expenses=operating_expenses,
            operating_profit=operating_profit,
            other_income=other_income,
            other_expenses=other_expenses,
            taxes=taxes,
            net_profit=net_profit,
            lines=lines,
        )

    def _sum_group(self, lines: list[PnLReportLine], group_name: str) -> Decimal:
        total = Decimal("0")
        for line in lines:
            if line.pnl_group == group_name:
                total += line.total
        return total