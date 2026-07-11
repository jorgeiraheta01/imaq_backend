from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

EstadoAlquiler = Literal["pendiente", "activo", "finalizado", "cancelado"]


class AlquilerBase(BaseModel):
    maquina_id: int
    operador_id: int | None = None
    fecha_inicio: date
    fecha_fin: date
    precio_acordado: Decimal


class AlquilerCreate(AlquilerBase):
    pass


class AlquilerUpdate(BaseModel):
    estado: EstadoAlquiler | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    costo_total: Decimal | None = None


class AlquilerOut(AlquilerBase):
    id: int
    arrendatario_id: int
    propietario_id: int
    costo_total: Decimal | None = None
    estado: EstadoAlquiler
    creado_en: datetime

    model_config = {"from_attributes": True}


class AlquilerPublicoOut(BaseModel):
    """Vista pública del historial de alquileres de una máquina: sin identidad
    del arrendatario ni precios, solo para mostrar actividad en el catálogo."""

    fecha_inicio: date
    fecha_fin: date
    estado: EstadoAlquiler

    model_config = {"from_attributes": True}
