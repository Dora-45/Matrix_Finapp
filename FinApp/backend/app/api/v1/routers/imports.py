from fastapi import APIRouter

router = APIRouter(prefix="/imports", tags=["Imports"])


@router.get("/status")
async def import_status():
    return {
        "module": "imports",
        "status": "ready",
        "message": "Модуль загрузки файлов подготовлен."
    }