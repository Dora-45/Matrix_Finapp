import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.bank_statement import BankStatementRow
from backend.app.services.bank_statement_validation_service import BankStatementValidationService
from backend.app.services.sber_statement_parser import parse_sber_statement

router = APIRouter(prefix="/imports", tags=["Imports"])

UPLOAD_DIR = Path(__file__).resolve().parents[5] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".xlsx", ".xls"}

_STATEMENT_COLUMNS = {c.key for c in BankStatementRow.__table__.columns}


@router.post("/bank-statement")
async def upload_bank_statement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Загружает банковскую выписку СберБизнес (.xlsx/.xls),
    парсит строки, валидирует и сохраняет в bank_statement_rows.
    Возвращает import_batch для дальнейшего review и проводки.
    """
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Разрешены только .xlsx и .xls файлы")

    import_batch = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{import_batch}{suffix}"

    content = await file.read()
    save_path.write_bytes(content)

    try:
        parsed_rows = parse_sber_statement(str(save_path))
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Ошибка парсинга файла: {e}")

    if not parsed_rows:
        raise HTTPException(
            status_code=422,
            detail="Не найдено ни одной операции. Проверь формат файла.",
        )

    validator = BankStatementValidationService()
    db_rows = []

    for i, row_data in enumerate(parsed_rows):
        safe_data = {k: v for k, v in row_data.items() if k in _STATEMENT_COLUMNS}
        row = BankStatementRow(
            import_batch=import_batch,
            source_file=file.filename,
            row_number=i + 1,
            **safe_data,
        )
        db_rows.append(row)

    validator.validate_rows(db_rows)
    db.add_all(db_rows)
    db.commit()

    valid_count = sum(1 for r in db_rows if r.validation_status == "valid")
    invalid_count = len(db_rows) - valid_count

    return {
        "import_batch": import_batch,
        "filename": file.filename,
        "total_rows": len(db_rows),
        "valid_rows": valid_count,
        "invalid_rows": invalid_count,
        "preview": [
            {
                "row_number": r.row_number,
                "date": str(r.operation_datetime),
                "direction": r.direction,
                "amount": str(r.amount),
                "account_type": r.account_type,
                "counterparty": r.counterparty_name,
                "purpose": (r.payment_purpose or "")[:80],
                "status": r.validation_status,
                "message": r.validation_message,
            }
            for r in db_rows[:10]
        ],
    }


@router.get("/status")
async def import_status():
    return {"module": "imports", "status": "ready"}
