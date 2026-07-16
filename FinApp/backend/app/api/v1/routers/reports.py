from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.cashflow import PnLReportResponse
from backend.app.services.pnl_service import PnlService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/pnl", response_model=PnLReportResponse)
def get_pnl_report(
    period_from: str,
    period_to: str,
    db: Session = Depends(get_db),
):
    service = PnlService(db)
    return service.get_report(period_from=period_from, period_to=period_to)


@router.get("/cashflow")
def get_cashflow_report():
    return {
        "report": "cashflow",
        "status": "stub",
        "message": "Cashflow report endpoint is ready for future implementation.",
    }