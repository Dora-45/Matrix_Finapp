from pydantic import BaseModel


class SettingCreate(BaseModel):
    key: str
    value: str
    description: str | None = None


class SettingRead(BaseModel):
    key: str
    value: str
    description: str | None = None

    model_config = {
        "from_attributes": True
    }