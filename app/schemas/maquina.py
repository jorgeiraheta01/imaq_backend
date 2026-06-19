from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

EstadoMaquina = Literal["disponible", "alquilada", "mantenimiento"]


class MaquinaBase(BaseModel):
    nombre: str
    tipo: str
    descripcion: str | None = None
    precio_dia: Decimal
    ubicacion: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None
    imagen_url: str | None = None
    departamento_id: int | None = None


class MaquinaCreate(MaquinaBase):
    pass


class MaquinaUpdate(BaseModel):
    nombre: str | None = None
    tipo: str | None = None
    descripcion: str | None = None
    precio_dia: Decimal | None = None
    ubicacion: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None
    imagen_url: str | None = None
    departamento_id: int | None = None
    estado: EstadoMaquina | None = None


class MaquinaOut(MaquinaBase):
    id: int
    propietario_id: int
    estado: EstadoMaquina
    creado_en: datetime

    model_config = {"from_attributes": True}
