from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Cotizacion(Base):
    """Negociación previa a un alquiler confirmado. Separada de `Alquiler`
    porque tiene su propia máquina de estados (contraoferta, rechazo,
    expiración) que no aplica a una reserva ya confirmada."""

    __tablename__ = "cotizaciones"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('pendiente','contraoferta','aceptada','rechazada','cancelada','expirada')",
            name="cotizaciones_estado_check",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    maquina_id: Mapped[int] = mapped_column(Integer, ForeignKey("maquinas.id"), nullable=False)
    arrendatario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    propietario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)

    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    precio_propuesto: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")

    # Contraoferta del propietario (nullable — solo se llenan si estado pasa por 'contraoferta')
    precio_contraoferta: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    fecha_inicio_contraoferta: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_fin_contraoferta: Mapped[date | None] = mapped_column(Date, nullable=True)
    notas_contraoferta: Mapped[str | None] = mapped_column(Text, nullable=True)

    motivo_rechazo: Mapped[str | None] = mapped_column(Text, nullable=True)
    alquiler_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("alquileres.id"), nullable=True)
    visto: Mapped[bool] = mapped_column(Boolean, default=False)
    visto_propietario: Mapped[bool] = mapped_column(Boolean, default=False)
    visto_arrendatario: Mapped[bool] = mapped_column(Boolean, default=False)

    # True solo cuando esta cotización fue auto-expirada porque OTRA cotización para la
    # misma máquina/fechas fue aceptada primero (ver aceptar_cotizacion). Se fija en el
    # momento exacto de la auto-expiración, no se deriva al leer — así no se confunde con
    # una expiración por timeout (72h sin respuesta), que deja esto en False.
    conflicto_fechas: Mapped[bool] = mapped_column(Boolean, default=False)

    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    fecha_respuesta: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fecha_expiracion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    maquina = relationship("Maquina")
    arrendatario = relationship("Usuario", foreign_keys=[arrendatario_id])
    propietario = relationship("Usuario", foreign_keys=[propietario_id])
    alquiler = relationship("Alquiler")
