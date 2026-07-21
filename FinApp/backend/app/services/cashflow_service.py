from datetime import date, datetime, time

from sqlalchemy.orm import Session

from backend.app.models.cashflow_operation import CashflowOperation
from backend.app.schemas.cashflow import CashflowReportLine, CashflowReportResponse


ACCOUNT_TYPES = ("checking", "credit", "personal")


class CashFlowService:
    def __init__(self, db: Session):
        self.db = db

    def build_report(
        self,
        date_from: date,
        date_to: date,
        account_types: list[str] | None = None,
        include_transfers: bool = False,
    ) -> CashflowReportResponse:
        """
        Строит отчёт ДДС за период с фильтрацией по счетам.

        account_types:
            список счетов: checking, credit, personal.
            Если None или пусто — включаются все (консолидированный отчёт).

        include_transfers:
            включать ли технические переводы между своими счетами.
            По умолчанию False, чтобы не задваивать оборот.
        """
        start_dt = datetime.combine(date_from, time.min)
        end_dt = datetime.combine(date_to, time.max)

        # Нормализуем список счетов
        selected_accounts = [a for a in (account_types or []) if a in ACCOUNT_TYPES]
        if not selected_accounts:
            selected_accounts = list(ACCOUNT_TYPES)

        query = (
            self.db.query(CashflowOperation)
            .filter(
                CashflowOperation.operation_datetime >= start_dt,
                CashflowOperation.operation_datetime <= end_dt,
                CashflowOperation.account_type.in_(selected_accounts),
            )
        )

        # По кредитной карте в ДДС учитываем только расходы.
        # Поступление кредита (credit + inflow) не включаем в отчёт,
        # чтобы не искажать управленческую картину.
        if "credit" in selected_accounts:
            query = query.filter(
                ~(
                    (CashflowOperation.account_type == "credit")
                    & (CashflowOperation.direction == "inflow")
                )
            )

        if not include_transfers:
            query = query.filter(CashflowOperation.section != "transfer")

        operations = query.all()

        grouped: dict[tuple[str, str, str], dict[str, float]] = {}

        for op in operations:
            section = op.section or "operating"
            direction = op.direction
            article = (
                op.article
                or ("Прочие поступления" if direction == "inflow" else "Прочие расходы")
            )
            key = (section, direction, article)

            if key not in grouped:
                grouped[key] = {"checking": 0.0, "credit": 0.0, "personal": 0.0}

            account_type = (
                op.account_type if op.account_type in ACCOUNT_TYPES else "checking"
            )
            grouped[key][account_type] += float(op.amount)

        lines: list[CashflowReportLine] = []
        for (section, direction, article), amounts in grouped.items():
            total = sum(amounts[a] for a in selected_accounts)
            lines.append(
                CashflowReportLine(
                    section=section,
                    direction=direction,
                    article=article,
                    total=round(total, 2),
                    checking=round(amounts["checking"], 2),
                    credit=round(amounts["credit"], 2),
                    personal=round(amounts["personal"], 2),
                )
            )

        inflow_lines = [l for l in lines if l.direction == "inflow"]
        outflow_lines = [l for l in lines if l.direction == "outflow"]

        total_inflow = round(sum(l.total for l in inflow_lines), 2)
        total_outflow = round(sum(l.total for l in outflow_lines), 2)
        net_cashflow = round(total_inflow - total_outflow, 2)

        net_checking = round(
            sum(l.checking for l in inflow_lines)
            - sum(l.checking for l in outflow_lines),
            2,
        )
        net_credit = round(
            sum(l.credit for l in inflow_lines)
            - sum(l.credit for l in outflow_lines),
            2,
        )
        net_personal = round(
            sum(l.personal for l in inflow_lines)
            - sum(l.personal for l in outflow_lines),
            2,
        )

        # Подсчёт неразобранных операций (без учёта inflow по кредиту)
        unclassified_query = (
            self.db.query(CashflowOperation)
            .filter(
                CashflowOperation.operation_datetime >= start_dt,
                CashflowOperation.operation_datetime <= end_dt,
                CashflowOperation.account_type.in_(selected_accounts),
                CashflowOperation.article == None,
            )
        )
        if "credit" in selected_accounts:
            unclassified_query = unclassified_query.filter(
                ~(
                    (CashflowOperation.account_type == "credit")
                    & (CashflowOperation.direction == "inflow")
                )
            )
        unclassified_count = unclassified_query.count()

        return CashflowReportResponse(
            period_from=str(date_from),
            period_to=str(date_to),
            accounts_included=selected_accounts,
            lines=lines,
            total_inflow=total_inflow,
            total_outflow=total_outflow,
            net_cashflow=net_cashflow,
            net_cashflow_checking=net_checking,
            net_cashflow_credit=net_credit,
            net_cashflow_personal=net_personal,
            unclassified_count=unclassified_count,
        )