from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FotoMaquina(Base):
    __tablename__ = "fotos_maquinas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    maquina_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("maquinas.id", ondelete="CASCADE"), nullable=False
    )
    url_cloudinary: Mapped[str] = mapped_column(String(500), nullable=False)
    public_id: Mapped[str] = mapped_column(String(200), nullable=False)
    es_principal: Mapped[bool] = mapped_column(Boolean, default=False)
    orden: Mapped[int] = mapped_column(Integer, default=0)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    maquina = relationship("Maquina", back_populates="fotos")
