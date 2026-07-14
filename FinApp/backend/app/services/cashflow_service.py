from datetime import date, datetime, time

from sqlalchemy.orm import Session

from backend.app.models.cashflow_operation import CashflowOperation
from backend.app.schemas.cashflow import CashflowReportLine, CashflowReportResponse


ACCOUNT_TYPES = ("checking", "credit", "personal")


class CashFlowService:
    def __init__(self, db: Session):
        self.db = db

    def build_report(self, date_from: date, date_to: date) -> CashflowReportResponse:
        start_dt = datetime.combine(date_from, time.min)
        end_dt = datetime.combine(date_to, time.max)

        operations = (
            self.db.query(CashflowOperation)
            .filter(
                CashflowOperation.operation_datetime >= start_dt,
                CashflowOperation.operation_datetime <= end_dt,
                CashflowOperation.section != "transfer",
            )
            .all()
        )

        grouped = {}

        for op in operations:
            section = op.section or "operating"
            direction = op.direction
            article = op.article or ("Прочие поступления" if direction == "inflow" else "Прочие расходы")
            key = (section, direction, article)

            if key not in grouped:
                grouped[key] = {
                    "checking": 0.0,
                    "credit": 0.0,
                    "personal": 0.0,
                }

            account_type = op.account_type if op.account_type in ACCOUNT_TYPES else "checking"
            grouped[key][account_type] += float(op.amount)

        lines = []
        for (section, direction, article), amounts in grouped.items():
            total = amounts["checking"] + amounts["credit"] + amounts["personal"]
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
            sum(l.checking for l in inflow_lines) - sum(l.checking for l in outflow_lines), 2
        )
        net_credit = round(
            sum(l.credit for l in inflow_lines) - sum(l.credit for l in outflow_lines), 2
        )
        net_personal = round(
            sum(l.personal for l in inflow_lines) - sum(l.personal for l in outflow_lines), 2
        )

        unclassified_count = (
            self.db.query(CashflowOperation)
            .filter(
                CashflowOperation.operation_datetime >= start_dt,
                CashflowOperation.operation_datetime <= end_dt,
                CashflowOperation.article == None,
            )
            .count()
        )

        return CashflowReportResponse(
            period_from=str(date_from),
            period_to=str(date_to),
            lines=lines,
            total_inflow=total_inflow,
            total_outflow=total_outflow,
            net_cashflow=net_cashflow,
            net_cashflow_checking=net_checking,
            net_cashflow_credit=net_credit,
            net_cashflow_personal=net_personal,
            unclassified_count=unclassified_count,
        )
