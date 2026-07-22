from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.v1.api import api_router
from backend.app.core.config import settings
from backend.app.db.base import Base
from backend.app.db.session import engine, SessionLocal

import backend.app.models


BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    # Заполняем справочник статей ДДС базовыми правилами, если он пуст.
    # Это нужно, чтобы автоклассификация и выпадающий список статей
    # работали сразу после первого запуска, без ручного заполнения БД.
    from backend.app.repositories.cashflow_category_repository import (
        CashflowCategoryRepository,
    )

    db = SessionLocal()
    try:
        CashflowCategoryRepository(db).seed_defaults()
    finally:
        db.close()

    print("\n=== REGISTERED ROUTES ===")
    for route in app.routes:
        methods = getattr(route, "methods", None)
        path = getattr(route, "path", None)
        if methods and path:
            print(sorted(methods), path)
    print("=== END ROUTES ===\n")

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(api_router)

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def root():
    html_file = FRONTEND_DIR / "finapp.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {
        "status": "ok",
        "message": "Frontend file not found, but API is running",
    }