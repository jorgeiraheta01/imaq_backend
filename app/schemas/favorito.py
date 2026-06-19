from datetime import datetime

from pydantic import BaseModel


class FavoritoBase(BaseModel):
    maquina_id: int


class FavoritoCreate(FavoritoBase):
    pass


class FavoritoOut(FavoritoBase):
    id: int
    usuario_id: int
    creado_en: datetime

    model_config = {"from_attributes": True}
