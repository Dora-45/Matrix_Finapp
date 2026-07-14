from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.cashflow_operation import CashflowOperation
from backend.app.schemas.bank_statement_review import (
    BankStatementBatchSummary,
    BankStatementRowRead,
    BankStatementRowUpdate,
    BatchActionResponse,
    BatchConfirmRequest,
    BatchPostRequest,
    CashflowOperationRead,
)
from backend.app.services.bank_statement_posting_service import (
    BankStatementPostingService,
)
from backend.app.services.bank_statement_review_service import (
    BankStatementReviewService,
)

router = APIRouter(prefix="/bank-statement-review", tags=["Bank Statement Review"])


@router.get("/rows", response_model=list[BankStatementRowRead])
def list_batch_rows(
    import_batch: str = Query(..., description="Идентификатор батча импорта"),
    confirmed_only: bool = Query(False),
    unconfirmed_only: bool = Query(False),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    service = BankStatementReviewService(db)
    return service.get_rows_by_batch(
        import_batch=import_batch,
        confirmed_only=confirmed_only,
        unconfirmed_only=unconfirmed_only,
        active_only=active_only,
    )


@router.get("/summary", response_model=BankStatementBatchSummary)
def get_batch_summary(
    import_batch: str = Query(..., description="Идентификатор батча импорта"),
    db: Session = Depends(get_db),
):
    service = BankStatementReviewService(db)
    return service.get_batch_summary(import_batch)


@router.patch("/rows/{row_id}", response_model=BankStatementRowRead)
def update_row(
    row_id: int,
    payload: BankStatementRowUpdate,
    db: Session = Depends(get_db),
):
    service = BankStatementReviewService(db)
    row = service.update_row(
        row_id=row_id,
        article=payload.article,
        project=payload.project,
        is_confirmed=payload.is_confirmed,
        is_deleted=payload.is_deleted,
    )

    if not row:
        raise HTTPException(status_code=404, detail="Строка не найдена")

    return row


@router.post("/confirm", response_model=BatchActionResponse)
def confirm_rows(
    payload: BatchConfirmRequest,
    db: Session = Depends(get_db),
):
    service = BankStatementReviewService(db)
    updated = service.confirm_rows(payload.row_ids)

    return BatchActionResponse(
        status="ok",
        message="Строки подтверждены",
        affected_count=updated,
    )


@router.post("/post", response_model=BatchActionResponse)
def post_batch(
    payload: BatchPostRequest,
    db: Session = Depends(get_db),
):
    service = BankStatementPostingService(db)
    result = service.post_confirmed_rows(payload.import_batch)

    return BatchActionResponse(
        status="ok",
        message=f"Батч {payload.import_batch} проведён",
        affected_count=result["posted_rows"],
    )


@router.get("/cashflow-operations", response_model=list[CashflowOperationRead])
def list_cashflow_operations(
    db: Session = Depends(get_db),
):
    return (
        db.query(CashflowOperation)
        .order_by(CashflowOperation.id.asc())
        .all()
    )