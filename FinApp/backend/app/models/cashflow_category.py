from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class CashflowCategory(Base):
    __tablename__ = "cashflow_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # operating | investing | financing | transfer
    section: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # inflow | outflow
    direction: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Название статьи ДДС
    article: Mapped[str] = mapped_column(String(100), nullable=False)

    # Ключевые слова через запятую
    keywords: Mapped[str] = mapped_column(Text, nullable=False)

    # all | checking | credit | personal
    account_type_filter: Mapped[str] = mapped_column(String(20), nullable=False, default="all")

    # Чем выше приоритет, тем раньше применяется правило
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)