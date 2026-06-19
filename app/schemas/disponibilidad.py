from datetime import date, datetime

from pydantic import BaseModel


class DisponibilidadBase(BaseModel):
    maquina_id: int
    fecha_inicio: date
    fecha_fin: date
    motivo: str | None = None


class DisponibilidadCreate(DisponibilidadBase):
    pass


class DisponibilidadUpdate(BaseModel):
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    motivo: str | None = None


class DisponibilidadOut(DisponibilidadBase):
    id: int
    creado_en: datetime

    model_config = {"from_attributes": True}
