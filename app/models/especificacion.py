from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Especificacion(Base):
    __tablename__ = "especificaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    maquina_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("maquinas.id", ondelete="CASCADE"), nullable=False
    )
    clave: Mapped[str] = mapped_column(String(50), nullable=False)
    valor: Mapped[str] = mapped_column(String(150), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    maquina = relationship("Maquina", back_populates="especificaciones")
