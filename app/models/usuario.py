from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint(
            "rol IN ('propietario','operador','arrendatario','admin')", name="usuarios_rol_check"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rol: Mapped[str] = mapped_column(String(20), nullable=False)
    verificado: Mapped[bool] = mapped_column(Boolean, default=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    sesiones = relationship("Sesion", back_populates="usuario")
    documentos_verificacion = relationship("DocumentoVerificacion", back_populates="usuario")
    maquinas = relationship("Maquina", back_populates="propietario")
    operador = relationship("Operador", back_populates="usuario", uselist=False)
    alquileres = relationship("Alquiler", back_populates="arrendatario")
    calificaciones = relationship("Calificacion", back_populates="usuario")
    favoritos = relationship("Favorito", back_populates="usuario")
    dispositivos = relationship("Dispositivo", back_populates="usuario")
