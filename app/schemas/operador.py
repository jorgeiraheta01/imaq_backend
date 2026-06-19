from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OperadorBase(BaseModel):
    usuario_id: int
    experiencia_anios: int = 0
    tarifa_dia: Decimal | None = None
    certificaciones: str | None = None


class OperadorCreate(OperadorBase):
    pass


class OperadorUpdate(BaseModel):
    experiencia_anios: int | None = None
    tarifa_dia: Decimal | None = None
    certificaciones: str | None = None
    verificado: bool | None = None


class OperadorOut(OperadorBase):
    id: int
    verificado: bool
    creado_en: datetime

    model_config = {"from_attributes": True}
