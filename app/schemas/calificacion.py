from datetime import datetime

from pydantic import BaseModel, Field


class CalificacionBase(BaseModel):
    maquina_id: int
    alquiler_id: int
    estrellas: int = Field(ge=1, le=5)
    comentario: str | None = None


class CalificacionCreate(CalificacionBase):
    pass


class CalificacionUpdate(BaseModel):
    estrellas: int | None = Field(default=None, ge=1, le=5)
    comentario: str | None = None


class CalificacionOut(CalificacionBase):
    id: int
    usuario_id: int
    creado_en: datetime

    model_config = {"from_attributes": True}
