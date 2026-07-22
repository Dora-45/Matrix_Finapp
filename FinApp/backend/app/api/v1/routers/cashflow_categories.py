from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.cashflow_category_repository import (
    CashflowCategoryRepository,
)

router = APIRouter(prefix="/cashflow-categories", tags=["Cashflow Categories"])


@router.get("/articles")
def list_articles(db: Session = Depends(get_db)):
    """
    Возвращает уникальный список названий статей ДДС из справочника категорий.
    Используется фронтендом (экран 'Проверка импорта') для выпадающего списка
    в поле 'Статья', чтобы не вводить название вручную каждый раз.
    """
    repo = CashflowCategoryRepository(db)
    categories = repo.get_all_active()
    articles = sorted({category.article for category in categories})
    return {"articles": articles}