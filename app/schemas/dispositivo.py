from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Plataforma = Literal["android", "ios", "web"]


class DispositivoBase(BaseModel):
    fcm_token: str
    plataforma: Plataforma = "android"


class DispositivoCreate(DispositivoBase):
    pass


class DispositivoOut(DispositivoBase):
    id: int
    usuario_id: int
    activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}
