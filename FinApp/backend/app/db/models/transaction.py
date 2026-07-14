from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, Boolean
from sqlalchemy.sql import func
from backend.app.db.base import Base

class Transaction(Base):
    """
    Таблица финансовых транзакций.
    Сюда попадают данные из банковских выписок и CRM.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Дата операции
    date = Column(Date, nullable=False, index=True)
    
    # Описание из банковской выписки
    description = Column(String(500), nullable=False)
    
    # Сумма (положительная = приход, отрицательная = расход)
    amount = Column(Float, nullable=False)
    
    # Валюта (по умолчанию RUB)
    currency = Column(String(3), default="RUB")
    
    # Категория статьи учёта (выручка, себестоимость, аренда и т.д.)
    category = Column(String(100), nullable=True, index=True)
    
    # Тип: income (приход) или expense (расход)
    transaction_type = Column(String(20), nullable=True, index=True)
    
    # Откуда данные: bank_csv, crm_api, manual
    source = Column(String(50), default="manual")
    
    # Счёт / контрагент
    counterparty = Column(String(200), nullable=True)
    
    # Флаг валидации (прошла ли транзакция проверки)
    is_validated = Column(Boolean, default=False)
    
    # Заметки для ручной корректировки
    notes = Column(Text, nullable=True)
    
    # Автоматические временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Transaction(id={self.id}, date={self.date}, amount={self.amount}, category={self.category})>"