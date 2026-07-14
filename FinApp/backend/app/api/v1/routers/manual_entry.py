from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.cashflow_operation import CashflowOperation
from backend.app.services.classification_service import ClassificationService

router = APIRouter(prefix="/manual", tags=["Manual Entry"])


class ManualOperationCreate(BaseModel):
    operation_date: str
    direction: str
    amount: float
    payment_purpose: str
    counterparty_name: str = ""
    article: str = ""


@router.post("/cashflow")
def add_manual_operation(
    payload: ManualOperationCreate,
    db: Session = Depends(get_db),
):
    op = CashflowOperation(
        operation_datetime=datetime.fromisoformat(payload.operation_date),
        account_number="personal",
        account_type="personal",
        direction=payload.direction,
        amount=Decimal(str(payload.amount)),
        currency="RUB",
        counterparty_name=payload.counterparty_name,
        payment_purpose=payload.payment_purpose,
        source_file="manual",
        source_sheet="manual",
        article=payload.article if payload.article else None,
        is_manual="yes",
    )

    db.add(op)
    db.commit()
    db.refresh(op)

    if not payload.article:
        svc = ClassificationService(db)
        svc.classify_all_unclassified()
        db.refresh(op)

    return {
        "status": "ok",
        "id": op.id,
        "article": op.article,
    }