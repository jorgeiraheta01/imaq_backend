from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Maquina(Base):
    __tablename__ = "maquinas"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('disponible','alquilada','mantenimiento')", name="maquinas_estado_check"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    propietario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    departamento_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departamentos.id"), nullable=True
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    precio_dia: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    ubicacion: Mapped[str | None] = mapped_column(String(150), nullable=True)
    latitud: Mapped[Decimal | None] = mapped_column(Numeric(10, 8), nullable=True)
    longitud: Mapped[Decimal | None] = mapped_column(Numeric(11, 8), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="disponible")
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    propietario = relationship("Usuario", back_populates="maquinas")
    departamento = relationship("Departamento", back_populates="maquinas")
    especificaciones = relationship("Especificacion", back_populates="maquina")
    disponibilidad = relationship("Disponibilidad", back_populates="maquina")
    fotos = relationship("FotoMaquina", back_populates="maquina")
    alquileres = relationship("Alquiler", back_populates="maquina")
    calificaciones = relationship("Calificacion", back_populates="maquina")
    favoritos = relationship("Favorito", back_populates="maquina")
