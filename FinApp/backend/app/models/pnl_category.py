from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class PnlCategory(Base):
    __tablename__ = "pnl_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # inflow | outflow
    direction: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # income | expense
    pnl_sign: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # revenue | cogs | operating_expenses | other_income | other_expenses | taxes
    pnl_group: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Название статьи ОПиУ
    pnl_article: Mapped[str] = mapped_column(String(100), nullable=False)

    # Ключевые слова через запятую
    keywords: Mapped[str] = mapped_column(Text, nullable=False)

    # all | checking | credit | personal
    account_type_filter: Mapped[str] = mapped_column(String(20), nullable=False, default="all")

    # Чем выше приоритет, тем раньше применяется правило
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)