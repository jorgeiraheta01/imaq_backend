from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Departamento(Base):
    __tablename__ = "departamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    pais: Mapped[str] = mapped_column(String(50), nullable=False, default="El Salvador")

    maquinas = relationship("Maquina", back_populates="departamento")
