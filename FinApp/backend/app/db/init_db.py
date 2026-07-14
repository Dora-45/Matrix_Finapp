from backend.app.db.base import Base, engine
from backend.app.db.models import Transaction, ReportSnapshot  # noqa: F401

def create_tables():
    """
    Создаёт все таблицы в базе данных.
    
    Вызывается при старте приложения.
    Если таблицы уже существуют — ничего не делает (безопасно).
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы базы данных созданы / проверены")