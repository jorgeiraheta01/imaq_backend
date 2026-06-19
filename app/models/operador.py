from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Operador(Base):
    __tablename__ = "operadores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    experiencia_anios: Mapped[int] = mapped_column(Integer, default=0)
    tarifa_dia: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    certificaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    verificado: Mapped[bool] = mapped_column(Boolean, default=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="operador")
    alquileres = relationship("Alquiler", back_populates="operador")
