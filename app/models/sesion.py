from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Sesion(Base):
    __tablename__ = "sesiones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(500), nullable=False)
    dispositivo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    expira_en: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="sesiones")
