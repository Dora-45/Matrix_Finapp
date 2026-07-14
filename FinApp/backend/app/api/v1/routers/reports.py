from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.cashflow_category_repository import CashflowCategoryRepository
from backend.app.schemas.cashflow import (
    CashflowCategoryCreate,
    CashflowCategoryRead,
    CashflowReportResponse,
)
from backend.app.services.cashflow_service import CashFlowService
from backend.app.services.classification_service import ClassificationService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/cashflow", response_model=CashflowReportResponse)
def get_cashflow_report(
    date_from: date = Query(..., description="Начало периода YYYY-MM-DD"),
    date_to: date = Query(..., description="Конец периода YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    service = CashFlowService(db)
    return service.build_report(date_from=date_from, date_to=date_to)


@router.post("/cashflow/classify")
def run_classification(db: Session = Depends(get_db)):
    service = ClassificationService(db)
    return service.classify_all_unclassified()


@router.post("/cashflow/reclassify")
def run_reclassification(db: Session = Depends(get_db)):
    service = ClassificationService(db)
    return service.reclassify_all()


@router.get("/cashflow/categories", response_model=list[CashflowCategoryRead])
def list_categories(db: Session = Depends(get_db)):
    repo = CashflowCategoryRepository(db)
    return repo.get_all_active()


@router.post("/cashflow/categories", response_model=CashflowCategoryRead)
def create_category(payload: CashflowCategoryCreate, db: Session = Depends(get_db)):
    repo = CashflowCategoryRepository(db)
    return repo.create(payload)


@router.post("/cashflow/categories/seed")
def seed_categories(db: Session = Depends(get_db)):
    repo = CashflowCategoryRepository(db)
    repo.seed_defaults()
    return {"status": "ok", "message": "Дефолтные категории загружены"}


@router.get("/pnl")
def get_pnl_report_stub():
    return {
        "report": "pnl",
        "status": "stub",
        "message": "ОПиУ будет на следующем этапе",
    }