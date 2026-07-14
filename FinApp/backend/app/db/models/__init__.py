# Импортируем все модели чтобы SQLAlchemy их "увидел" при создании таблиц
from backend.app.db.models.transaction import Transaction
from backend.app.db.models.report_snapshot import ReportSnapshot