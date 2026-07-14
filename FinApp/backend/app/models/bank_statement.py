from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class BankStatementRow(Base):
    __tablename__ = "bank_statement_rows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    import_batch: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_sheet: Mapped[str | None] = mapped_column(String(255), nullable=True)
    row_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    operation_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    account_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    account_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    direction: Mapped[str | None] = mapped_column(String(10), nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True, default="RUB")

    counterparty_account: Mapped[str | None] = mapped_column(String(64), nullable=True)
    counterparty_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    document_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    operation_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    payment_purpose: Mapped[str | None] = mapped_column(Text, nullable=True)

    article: Mapped[str | None] = mapped_column(String(100), nullable=True)
    project: Mapped[str | None] = mapped_column(String(100), nullable=True)

    validation_status: Mapped[str] = mapped_column(String(20), nullable=False, default="new")
    validation_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_confirmed: Mapped[str] = mapped_column(String(10), nullable=False, default="no")
    is_deleted: Mapped[str] = mapped_column(String(10), nullable=False, default="no")