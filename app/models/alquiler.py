from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Alquiler(Base):
    __tablename__ = "alquileres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    maquina_id: Mapped[int] = mapped_column(Integer, ForeignKey("maquinas.id"), nullable=False)
    cliente_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    operador_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("operadores.id"), nullable=True)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    costo_total: Mapped[float] = mapped_column(Float, nullable=False)
    estado: Mapped[str] = mapped_column(String(30), default="pendiente")
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    maquina = relationship("Maquina", back_populates="alquileres")
    cliente = relationship("Usuario", back_populates="alquileres")
    operador = relationship("Operador", back_populates="alquileres")
