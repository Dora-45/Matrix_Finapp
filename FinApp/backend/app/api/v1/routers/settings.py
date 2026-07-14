from fastapi import APIRouter

from backend.app.core.config import settings

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("")
async def get_settings_info():
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "debug": settings.debug,
        "database_url": settings.database_url,
    }