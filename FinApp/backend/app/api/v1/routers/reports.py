from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.cashflow import CashflowReportResponse, PnLReportResponse
from backend.app.services.cashflow_service import CashFlowService
from backend.app.services.pnl_service import PnlService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/cashflow", response_model=CashflowReportResponse)
def get_cashflow_report(
    date_from: date = Query(..., description="Начало периода YYYY-MM-DD"),
    date_to: date = Query(..., description="Конец периода YYYY-MM-DD"),
    account_types: list[str] | None = Query(
        None,
        description=(
            "Счета для включения в отчёт: checking, credit, personal. "
            "Если не указано — отчёт по всем счетам (консолидированный)."
        ),
    ),
    include_transfers: bool = Query(
        False,
        description=(
            "Включать технические переводы между своими счетами. "
            "По умолчанию выключено, чтобы не задваивать оборот."
        ),
    ),
    db: Session = Depends(get_db),
):
    service = CashFlowService(db)
    return service.build_report(
        date_from=date_from,
        date_to=date_to,
        account_types=account_types,
        include_transfers=include_transfers,
    )


@router.get("/pnl", response_model=PnLReportResponse)
def get_pnl_report(
    period_from: str,
    period_to: str,
    db: Session = Depends(get_db),
):
    service = PnlService(db)
    return service.get_report(period_from=period_from, period_to=period_to)