from backend.app.db.base import Base, engine
from backend.app.db.models import ReportSnapshot, Transaction  # noqa: F401
from backend.app.models import (  # noqa: F401
    BankStatementRow,
    CashflowCategory,
    CashflowOperation,
    PnlCategory,
    Setting,
)


def create_tables():
    """
    Создаёт все таблицы в базе данных.

    Вызывается при старте приложения.
    Если таблицы уже существуют — ничего не делает.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы базы данных созданы / проверены")