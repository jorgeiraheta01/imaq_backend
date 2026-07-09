from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

Rol = Literal["propietario", "operador", "arrendatario", "admin"]
RolRegistro = Literal["propietario", "operador", "arrendatario"]

CLOUDINARY_PREFIX = "https://res.cloudinary.com/dunj6mccp/"


def _validar_cloudinary_url(v: str | None) -> str | None:
    if v and not v.startswith(CLOUDINARY_PREFIX):
        raise ValueError(f"foto_url debe ser una URL de Cloudinary válida ({CLOUDINARY_PREFIX}...)")
    return v


class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str | None = None
    rol: Rol


class UsuarioCreate(UsuarioBase):
    rol: RolRegistro
    password: str = Field(min_length=8)
    dui: str = Field(pattern=r"^[0-9]{8}-[0-9]{1}$", description="DUI salvadoreño, ej: 01234567-8")


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    telefono: str | None = None
    foto_url: str | None = None
    verificado: bool | None = None

    @field_validator("foto_url")
    @classmethod
    def validar_foto_url(cls, v: str | None) -> str | None:
        return _validar_cloudinary_url(v)


class UsuarioOut(UsuarioBase):
    id: int
    foto_url: str | None = None
    verificado: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


class UsuarioPublicoOut(BaseModel):
    id: int
    nombre: str
    telefono: str | None = None
    foto_url: str | None = None
    rol: Rol
    verificado: bool

    model_config = {"from_attributes": True}


class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str = Field(min_length=8)
