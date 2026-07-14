from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    filename: str
    saved_as: str
    rows_preview: list[dict]
    columns: list[str]
    total_rows: int
    source_type: str