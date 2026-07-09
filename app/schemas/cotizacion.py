from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

EstadoCotizacion = Literal["pendiente", "contraoferta", "aceptada", "rechazada", "cancelada", "expirada"]


class CotizacionCreate(BaseModel):
    maquina_id: int
    fecha_inicio: date
    fecha_fin: date
    precio_propuesto: Decimal
    notas: str | None = None


class CotizacionRechazar(BaseModel):
    motivo_rechazo: str | None = None


class CotizacionContraoferta(BaseModel):
    precio_contraoferta: Decimal
    fecha_inicio_contraoferta: date | None = None
    fecha_fin_contraoferta: date | None = None
    notas_contraoferta: str | None = None


class CotizacionOut(BaseModel):
    id: int
    maquina_id: int
    arrendatario_id: int
    propietario_id: int
    fecha_inicio: date
    fecha_fin: date
    precio_propuesto: Decimal
    notas: str | None = None
    estado: EstadoCotizacion

    precio_contraoferta: Decimal | None = None
    fecha_inicio_contraoferta: date | None = None
    fecha_fin_contraoferta: date | None = None
    notas_contraoferta: str | None = None

    motivo_rechazo: str | None = None
    alquiler_id: int | None = None
    visto: bool
    visto_propietario: bool = False
    visto_arrendatario: bool = False

    fecha_creacion: datetime
    fecha_respuesta: datetime | None = None
    fecha_expiracion: datetime | None = None

    # Denormalized for display without an extra lookup (arrendatario's own
    # profile isn't otherwise fetchable by the propietario viewing "recibidas").
    arrendatario_nombre: str
    arrendatario_telefono: str | None = None

    # Only populated by PATCH /aceptar: warns of an overlapping accepted
    # alquiler for the same máquina without blocking the acceptance.
    conflicto_fechas: bool = False

    model_config = {"from_attributes": True}
