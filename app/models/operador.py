from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Operador(Base):
    __tablename__ = "operadores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    especialidad: Mapped[str | None] = mapped_column(String(150), nullable=True)
    anios_experiencia: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tarifa_por_dia: Mapped[float | None] = mapped_column(Float, nullable=True)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    alquileres = relationship("Alquiler", back_populates="operador")
