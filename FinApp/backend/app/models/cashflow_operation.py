from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class CashflowOperation(Base):
    __tablename__ = "cashflow_operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    operation_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    account_number: Mapped[str] = mapped_column(String(64), nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # checking | credit | personal

    direction: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # inflow | outflow
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="RUB")

    counterparty_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment_purpose: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_sheet: Mapped[str | None] = mapped_column(String(255), nullable=True)

    article: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # Временно используем для секции ДДС:
    # operating | investing | financing | transfer
    project: Mapped[str | None] = mapped_column(String(100), nullable=True)

    is_manual: Mapped[str | None] = mapped_column(String(10), nullable=True)