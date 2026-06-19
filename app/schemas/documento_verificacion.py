from datetime import datetime
from typing import Literal

from pydantic import BaseModel

TipoDocumento = Literal["dui", "licencia", "rtn", "certificacion"]
EstadoDocumento = Literal["pendiente", "aprobado", "rechazado"]


class DocumentoVerificacionBase(BaseModel):
    usuario_id: int
    tipo: TipoDocumento
    url_documento: str


class DocumentoVerificacionCreate(DocumentoVerificacionBase):
    pass


class DocumentoVerificacionUpdate(BaseModel):
    estado: EstadoDocumento | None = None


class DocumentoVerificacionOut(DocumentoVerificacionBase):
    id: int
    estado: EstadoDocumento
    creado_en: datetime

    model_config = {"from_attributes": True}
