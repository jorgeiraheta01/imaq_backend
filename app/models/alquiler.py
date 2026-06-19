from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Alquiler(Base):
    __tablename__ = "alquileres"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('pendiente','activo','finalizado','cancelado')",
            name="alquileres_estado_check",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    maquina_id: Mapped[int] = mapped_column(Integer, ForeignKey("maquinas.id"), nullable=False)
    arrendatario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    operador_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("operadores.id"), nullable=True
    )
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    precio_acordado: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    costo_total: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    maquina = relationship("Maquina", back_populates="alquileres")
    arrendatario = relationship("Usuario", back_populates="alquileres")
    operador = relationship("Operador", back_populates="alquileres")
    calificaciones = relationship("Calificacion", back_populates="alquiler")
