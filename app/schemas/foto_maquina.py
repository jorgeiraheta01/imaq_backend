from datetime import datetime

from pydantic import BaseModel


class FotoMaquinaBase(BaseModel):
    maquina_id: int
    url_cloudinary: str
    public_id: str
    es_principal: bool = False
    orden: int = 0


class FotoMaquinaCreate(FotoMaquinaBase):
    pass


class FotoMaquinaOut(FotoMaquinaBase):
    id: int
    creado_en: datetime

    model_config = {"from_attributes": True}
