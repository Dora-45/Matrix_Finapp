from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
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
    # По умолчанию личный счёт, так как ручной ввод в первую очередь
    # закрывает операции, которые не приходят из банковской выписки
    # (например, оплаты с личной карты владельца бизнеса).
    account_type: str = "personal"
    account_number: str = "personal"
    section: str = "operating"


class ManualOperationUpdate(BaseModel):
    operation_date: Optional[str] = None
    direction: Optional[str] = None
    amount: Optional[float] = None
    payment_purpose: Optional[str] = None
    counterparty_name: Optional[str] = None
    article: Optional[str] = None
    account_type: Optional[str] = None
    section: Optional[str] = None


@router.post("/cashflow")
def add_manual_operation(
    payload: ManualOperationCreate,
    db: Session = Depends(get_db),
):
    if payload.account_type not in {"checking", "credit", "personal"}:
        raise HTTPException(status_code=400, detail="account_type должен быть checking, credit или personal")

    op = CashflowOperation(
        operation_datetime=datetime.fromisoformat(payload.operation_date),
        account_number=payload.account_number,
        account_type=payload.account_type,
        direction=payload.direction,
        amount=Decimal(str(payload.amount)),
        currency="RUB",
        counterparty_name=payload.counterparty_name,
        payment_purpose=payload.payment_purpose,
        source_file="manual",
        source_sheet="manual",
        article=payload.article if payload.article else None,
        section=payload.section,
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
        "account_type": op.account_type,
    }


@router.get("/cashflow")
def list_manual_operations(db: Session = Depends(get_db)):
    """Список всех ручных записей (включая записи по личному счёту)."""
    return (
        db.query(CashflowOperation)
        .filter(CashflowOperation.is_manual == "yes")
        .order_by(CashflowOperation.operation_datetime.desc())
        .all()
    )


@router.patch("/cashflow/{operation_id}")
def update_operation(
    operation_id: int,
    payload: ManualOperationUpdate,
    db: Session = Depends(get_db),
):
    """
    Редактирование суммы, статьи, счёта или назначения уже проведённой
    операции ДДС — как ручных записей, так и строк, попавших из выписки.
    Это то место, где можно исправить сумму в ведомости или переставить
    операцию с расчётного счёта на кредитный (и наоборот).
    """
    op = db.query(CashflowOperation).filter(CashflowOperation.id == operation_id).first()
    if not op:
        raise HTTPException(status_code=404, detail="Операция не найдена")

    if payload.operation_date is not None:
        op.operation_datetime = datetime.fromisoformat(payload.operation_date)

    if payload.direction is not None:
        op.direction = payload.direction

    if payload.amount is not None:
        op.amount = Decimal(str(payload.amount))

    if payload.payment_purpose is not None:
        op.payment_purpose = payload.payment_purpose

    if payload.counterparty_name is not None:
        op.counterparty_name = payload.counterparty_name

    if payload.article is not None:
        op.article = payload.article

    if payload.account_type is not None:
        if payload.account_type not in {"checking", "credit", "personal"}:
            raise HTTPException(status_code=400, detail="account_type должен быть checking, credit или personal")
        op.account_type = payload.account_type

    if payload.section is not None:
        op.section = payload.section

    db.commit()
    db.refresh(op)

    return {
        "status": "ok",
        "id": op.id,
        "amount": str(op.amount),
        "account_type": op.account_type,
        "article": op.article,
    }


@router.delete("/cashflow/{operation_id}")
def delete_operation(
    operation_id: int,
    db: Session = Depends(get_db),
):
    op = db.query(CashflowOperation).filter(CashflowOperation.id == operation_id).first()
    if not op:
        raise HTTPException(status_code=404, detail="Операция не найдена")

    db.delete(op)
    db.commit()

    return {"status": "ok", "deleted_id": operation_id}