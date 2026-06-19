from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Calificacion(Base):
    __tablename__ = "calificaciones"
    __table_args__ = (
        CheckConstraint("estrellas BETWEEN 1 AND 5", name="calificaciones_estrellas_check"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    maquina_id: Mapped[int] = mapped_column(Integer, ForeignKey("maquinas.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    alquiler_id: Mapped[int] = mapped_column(Integer, ForeignKey("alquileres.id"), nullable=False)
    estrellas: Mapped[int] = mapped_column(Integer, nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    maquina = relationship("Maquina", back_populates="calificaciones")
    usuario = relationship("Usuario", back_populates="calificaciones")
    alquiler = relationship("Alquiler", back_populates="calificaciones")
