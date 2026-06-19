from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

Rol = Literal["propietario", "operador", "arrendatario", "admin"]


class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str | None = None
    rol: Rol


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    telefono: str | None = None
    foto_url: str | None = None
    verificado: bool | None = None


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
