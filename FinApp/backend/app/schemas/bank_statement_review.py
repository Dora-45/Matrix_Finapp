from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class BankStatementRowRead(BaseModel):
    id: int
    import_batch: str | None = None
    operation_datetime: datetime | None = None
    account_number: str | None = None
    account_type: str | None = None
    direction: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    counterparty_account: str | None = None
    counterparty_name: str | None = None
    bank_name: str | None = None
    document_number: str | None = None
    operation_code: str | None = None
    payment_purpose: str | None = None
    article: str | None = None
    project: str | None = None
    validation_status: str | None = None
    validation_message: str | None = None
    is_confirmed: str | None = None
    is_deleted: str | None = None
    source_file: str | None = None
    source_sheet: str | None = None

    model_config = {"from_attributes": True}


class BankStatementRowUpdate(BaseModel):
    article: Optional[str] = None
    project: Optional[str] = None
    account_type: Optional[str] = None
    amount: Optional[Decimal] = None
    is_confirmed: Optional[str] = None
    is_deleted: Optional[str] = None


class BatchConfirmRequest(BaseModel):
    row_ids: list[int]


class BatchPostRequest(BaseModel):
    import_batch: str


class BatchActionResponse(BaseModel):
    status: str
    message: str
    affected_count: int


class BankStatementBatchSummary(BaseModel):
    import_batch: str
    total_rows: int
    confirmed_rows: int
    deleted_rows: int
    valid_rows: int
    invalid_rows: int


class CashflowOperationRead(BaseModel):
    id: int
    operation_datetime: datetime
    account_number: str
    account_type: str
    direction: str
    amount: Decimal
    currency: str
    counterparty_name: str | None = None
    payment_purpose: str | None = None
    article: str | None = None
    project: str | None = None
    source_file: str | None = None
    source_sheet: str | None = None
    is_manual: str | None = None

    model_config = {"from_attributes": True}