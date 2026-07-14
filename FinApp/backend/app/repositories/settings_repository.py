from sqlalchemy.orm import Session

from backend.app.models.setting import Setting
from backend.app.schemas.setting import SettingCreate


class SettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Setting]:
        return self.db.query(Setting).order_by(Setting.key.asc()).all()

    def get_by_key(self, key: str) -> Setting | None:
        return self.db.query(Setting).filter(Setting.key == key).first()

    def upsert(self, data: SettingCreate) -> Setting:
        setting = self.get_by_key(data.key)

        if setting is None:
            setting = Setting(
                key=data.key,
                value=data.value,
                description=data.description
            )
            self.db.add(setting)
        else:
            setting.value = data.value
            setting.description = data.description

        self.db.commit()
        self.db.refresh(setting)
        return setting