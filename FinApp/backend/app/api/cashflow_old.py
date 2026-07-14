from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.cashflow_operation import CashflowOperation
from backend.app.schemas.cashflow import (
    CashflowNormalizePreview,
    CashflowNormalizeResponse,
)
from backend.app.services.sber_statement_parser import parse_sber_statement

router = APIRouter(prefix="/api/v1/cashflow", tags=["cashflow"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".xlsx", ".xls"}


@router.post("/normalize-bank-statement", response_model=CashflowNormalizeResponse)
async def normalize_bank_statement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Файл не выбран")

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Для банковской выписки сейчас поддерживаются .xlsx и .xls"
        )

    safe_name = f"{uuid4().hex}_{file.filename}"
    save_path = UPLOAD_DIR / safe_name
    save_path.write_bytes(await file.read())

    try:
        normalized_rows = parse_sber_statement(str(save_path))
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка разбора выписки: {str(error)}"
        )

    if not normalized_rows:
        raise HTTPException(
            status_code=400,
            detail="Не удалось найти операции в выписке"
        )

    inserted = []
    for item in normalized_rows:
        operation = CashflowOperation(**item)
        db.add(operation)
        inserted.append(operation)

    db.commit()

    preview = [
        CashflowNormalizePreview(
            account_number=item["account_number"],
            account_type=item["account_type"],
            operation_datetime=item["operation_datetime"].isoformat(),
            direction=item["direction"],
            amount=float(item["amount"]),
            counterparty_name=item["counterparty_name"],
            payment_purpose=item["payment_purpose"],
        )
        for item in normalized_rows[:10]
    ]

    return CashflowNormalizeResponse(
        filename=file.filename,
        imported_rows=len(normalized_rows),
        sheets_processed=len({row["source_sheet"] for row in normalized_rows}),
        preview=preview,
    )