from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

EstadoMaquina = Literal["disponible", "alquilada", "mantenimiento"]
TipoPrecio = Literal["hora", "dia"]


class MaquinaBase(BaseModel):
    nombre: str
    tipo: str
    descripcion: str | None = None
    precio_dia: Decimal
    tipo_precio: TipoPrecio = "dia"
    ubicacion: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None
    imagen_url: str | None = None
    marca: str | None = None
    capacidad: str | None = None
    año: int | None = None
    horometro: str | None = None
    incluye_operador: bool = False
    incluye_combustible: bool = False
    telefono_contacto: str | None = None
    nombre_contacto: str | None = None
    departamento_id: int | None = None


class MaquinaCreate(MaquinaBase):
    pass


class MaquinaUpdate(BaseModel):
    nombre: str | None = None
    tipo: str | None = None
    descripcion: str | None = None
    precio_dia: Decimal | None = None
    tipo_precio: TipoPrecio | None = None
    ubicacion: str | None = None
    latitud: Decimal | None = None
    longitud: Decimal | None = None
    imagen_url: str | None = None
    marca: str | None = None
    capacidad: str | None = None
    año: int | None = None
    horometro: str | None = None
    incluye_operador: bool | None = None
    incluye_combustible: bool | None = None
    telefono_contacto: str | None = None
    nombre_contacto: str | None = None
    departamento_id: int | None = None
    estado: EstadoMaquina | None = None


class MaquinaOut(MaquinaBase):
    id: int
    propietario_id: int
    estado: EstadoMaquina
    creado_en: datetime

    model_config = {"from_attributes": True}
