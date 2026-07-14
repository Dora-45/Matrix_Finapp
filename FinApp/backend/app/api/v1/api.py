from fastapi import APIRouter

from backend.app.api.v1.routers import (
    bank_statement_review,
    health,
    imports,
    manual_entry,
    reports,
    settings,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(imports.router)
api_router.include_router(settings.router)
api_router.include_router(reports.router)
api_router.include_router(manual_entry.router)
api_router.include_router(bank_statement_review.router)