from pathlib import Path
from uuid import uuid4

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.schemas.import_file import FileUploadResponse

router = APIRouter(prefix="/api/v1/imports", tags=["imports"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def read_uploaded_table(file_path: Path) -> pd.DataFrame:
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        try:
            return pd.read_csv(file_path)
        except UnicodeDecodeError:
            return pd.read_csv(file_path, encoding="cp1251")
    elif suffix in {".xlsx", ".xls"}:
        return pd.read_excel(file_path)

    raise ValueError("Неподдерживаемый формат файла")


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Файл не выбран")

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Разрешены только файлы .csv, .xlsx, .xls"
        )

    safe_name = f"{uuid4().hex}_{file.filename}"
    save_path = UPLOAD_DIR / safe_name

    content = await file.read()
    save_path.write_bytes(content)

    try:
        df = read_uploaded_table(save_path)
    except Exception as error:
        if save_path.exists():
            save_path.unlink()
        raise HTTPException(
            status_code=400,
            detail=f"Не удалось прочитать файл: {str(error)}"
        )

    df = df.fillna("")

    preview_rows = df.head(10).to_dict(orient="records")
    columns = [str(column) for column in df.columns.tolist()]

    return FileUploadResponse(
        filename=file.filename,
        saved_as=safe_name,
        rows_preview=preview_rows,
        columns=columns,
        total_rows=len(df),
        source_type=extension.replace(".", "")
    )