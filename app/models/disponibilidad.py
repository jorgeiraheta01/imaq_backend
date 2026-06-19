from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Disponibilidad(Base):
    __tablename__ = "disponibilidad"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    maquina_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("maquinas.id", ondelete="CASCADE"), nullable=False
    )
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    motivo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    maquina = relationship("Maquina", back_populates="disponibilidad")
