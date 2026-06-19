from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Maquina(Base):
    __tablename__ = "maquinas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    marca: Mapped[str | None] = mapped_column(String(100), nullable=True)
    modelo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    anio: Mapped[int | None] = mapped_column(Integer, nullable=True)
    precio_por_dia: Mapped[float] = mapped_column(Float, nullable=False)
    ubicacion: Mapped[str | None] = mapped_column(String(200), nullable=True)
    disponible: Mapped[bool] = mapped_column(default=True)
    propietario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    propietario = relationship("Usuario", back_populates="maquinas")
    alquileres = relationship("Alquiler", back_populates="maquina")
