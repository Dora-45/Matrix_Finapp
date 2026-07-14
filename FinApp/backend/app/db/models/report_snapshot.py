from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from backend.app.db.base import Base

class ReportSnapshot(Base):
    """
    Сохранённые версии отчётов (кеш результатов расчёта).
    Позволяет быстро загружать последний расчёт без пересчёта.
    """
    __tablename__ = "report_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    
    # Тип отчёта: pnl, cashflow, salary, profitability
    report_type = Column(String(50), nullable=False, index=True)
    
    # Период: 2024-01, 2024-Q1, 2024 (месяц, квартал, год)
    period = Column(String(20), nullable=False, index=True)
    
    # JSON с данными отчёта
    data = Column(JSON, nullable=False)
    
    # Статус: calculating, ready, error
    status = Column(String(20), default="ready")
    
    # Сообщение об ошибке (если status=error)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ReportSnapshot(type={self.report_type}, period={self.period})>"