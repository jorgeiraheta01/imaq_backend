from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Dispositivo(Base):
    __tablename__ = "dispositivos"
    __table_args__ = (
        CheckConstraint("plataforma IN ('android','ios','web')", name="dispositivos_plataforma_check"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    fcm_token: Mapped[str] = mapped_column(String(500), nullable=False)
    plataforma: Mapped[str] = mapped_column(String(20), default="android")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="dispositivos")
