from datetime import date, datetime

from pydantic import BaseModel, EmailStr


# ---------- Usuario ----------
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str | None = None
    es_proveedor: bool = False


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioOut(UsuarioBase):
    id: int
    activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


# ---------- Auth ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- Maquina ----------
class MaquinaBase(BaseModel):
    nombre: str
    tipo: str
    descripcion: str | None = None
    marca: str | None = None
    modelo: str | None = None
    anio: int | None = None
    precio_por_dia: float
    ubicacion: str | None = None
    disponible: bool = True


class MaquinaCreate(MaquinaBase):
    pass


class MaquinaUpdate(BaseModel):
    nombre: str | None = None
    tipo: str | None = None
    descripcion: str | None = None
    marca: str | None = None
    modelo: str | None = None
    anio: int | None = None
    precio_por_dia: float | None = None
    ubicacion: str | None = None
    disponible: bool | None = None


class MaquinaOut(MaquinaBase):
    id: int
    propietario_id: int
    creado_en: datetime

    model_config = {"from_attributes": True}


# ---------- Operador ----------
class OperadorBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str | None = None
    especialidad: str | None = None
    anios_experiencia: int | None = None
    tarifa_por_dia: float | None = None
    disponible: bool = True


class OperadorCreate(OperadorBase):
    pass


class OperadorUpdate(BaseModel):
    nombre: str | None = None
    telefono: str | None = None
    especialidad: str | None = None
    anios_experiencia: int | None = None
    tarifa_por_dia: float | None = None
    disponible: bool | None = None


class OperadorOut(OperadorBase):
    id: int
    creado_en: datetime

    model_config = {"from_attributes": True}


# ---------- Alquiler ----------
class AlquilerBase(BaseModel):
    maquina_id: int
    operador_id: int | None = None
    fecha_inicio: date
    fecha_fin: date


class AlquilerCreate(AlquilerBase):
    pass


class AlquilerUpdate(BaseModel):
    estado: str | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None


class AlquilerOut(AlquilerBase):
    id: int
    cliente_id: int
    costo_total: float
    estado: str
    creado_en: datetime

    model_config = {"from_attributes": True}
