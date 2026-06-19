from datetime import datetime

from pydantic import BaseModel


class EspecificacionBase(BaseModel):
    maquina_id: int
    clave: str
    valor: str


class EspecificacionCreate(EspecificacionBase):
    pass


class EspecificacionOut(EspecificacionBase):
    id: int
    creado_en: datetime

    model_config = {"from_attributes": True}
