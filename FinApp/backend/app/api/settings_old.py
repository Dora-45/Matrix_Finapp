from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.settings_repository import SettingsRepository
from backend.app.schemas.setting import SettingCreate, SettingRead

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


@router.get("/", response_model=list[SettingRead])
def list_settings(db: Session = Depends(get_db)):
    repository = SettingsRepository(db)
    return repository.get_all()


@router.post("/", response_model=SettingRead)
def create_or_update_setting(
    payload: SettingCreate,
    db: Session = Depends(get_db)
):
    repository = SettingsRepository(db)
    return repository.upsert(payload)