from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DocumentoVerificacion(Base):
    __tablename__ = "documentos_verificacion"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('dui','licencia','rtn','certificacion')",
            name="documentos_verificacion_tipo_check",
        ),
        CheckConstraint(
            "estado IN ('pendiente','aprobado','rechazado')",
            name="documentos_verificacion_estado_check",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    url_documento: Mapped[str] = mapped_column(String(500), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="documentos_verificacion")
