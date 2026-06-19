from datetime import datetime

from pydantic import BaseModel


class SesionBase(BaseModel):
    usuario_id: int
    token: str
    dispositivo: str | None = None
    expira_en: datetime


class SesionCreate(SesionBase):
    pass


class SesionOut(SesionBase):
    id: int
    activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}
