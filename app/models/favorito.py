from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Favorito(Base):
    __tablename__ = "favoritos"
    __table_args__ = (UniqueConstraint("usuario_id", "maquina_id", name="favoritos_usuario_id_maquina_id_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    maquina_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("maquinas.id", ondelete="CASCADE"), nullable=False
    )
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="favoritos")
    maquina = relationship("Maquina", back_populates="favoritos")
