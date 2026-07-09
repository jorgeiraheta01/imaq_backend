from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.cotizacion import Cotizacion
from app.models.disponibilidad import Disponibilidad
from app.models.maquina import Maquina
from app.models.usuario import Usuario
from app.rate_limit import limiter
from app.schemas.maquina import MaquinaCreate, MaquinaOut, MaquinaUpdate


class BloqueDisponibilidad(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    motivo: str

router = APIRouter(prefix="/maquinas", tags=["Máquinas"])

OrdenMaquina = Literal["precio_asc", "precio_desc", "reciente"]


@router.get("/", response_model=list[MaquinaOut])
def listar_maquinas(
    skip: int = 0,
    limit: int = 100,
    buscar: str | None = None,
    estado: str | None = None,
    tipo: str | None = None,
    departamento_id: int | None = None,
    precio_max: float | None = None,
    tipo_precio: str | None = None,
    incluye_operador: bool | None = None,
    orden: OrdenMaquina | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Maquina)

    if buscar:
        patron = f"%{buscar}%"
        query = query.filter(
            or_(
                Maquina.nombre.ilike(patron),
                Maquina.descripcion.ilike(patron),
                Maquina.marca.ilike(patron),
                Maquina.ubicacion.ilike(patron),
                Maquina.nombre_contacto.ilike(patron),
            )
        )
    if estado:
        query = query.filter(Maquina.estado == estado)
    if tipo:
        query = query.filter(Maquina.tipo.ilike(f"%{tipo}%"))
    if departamento_id is not None:
        query = query.filter(Maquina.departamento_id == departamento_id)
    if precio_max is not None:
        query = query.filter(Maquina.precio_dia <= precio_max)
    if tipo_precio:
        query = query.filter(Maquina.tipo_precio == tipo_precio)
    if incluye_operador is not None:
        query = query.filter(Maquina.incluye_operador == incluye_operador)

    if orden == "precio_asc":
        query = query.order_by(Maquina.precio_dia.asc())
    elif orden == "precio_desc":
        query = query.order_by(Maquina.precio_dia.desc())
    elif orden == "reciente":
        query = query.order_by(Maquina.creado_en.desc())

    return query.offset(skip).limit(limit).all()


@router.get("/{maquina_id}", response_model=MaquinaOut)
def obtener_maquina(maquina_id: int, db: Session = Depends(get_db)):
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    return maquina


@router.post("/", response_model=MaquinaOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
def crear_maquina(
    request: Request,
    maquina: MaquinaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    nueva_maquina = Maquina(**maquina.model_dump(), propietario_id=usuario_actual.id)
    db.add(nueva_maquina)
    db.commit()
    db.refresh(nueva_maquina)
    return nueva_maquina


@router.put("/{maquina_id}", response_model=MaquinaOut)
def actualizar_maquina(
    maquina_id: int,
    datos: MaquinaUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    if maquina.propietario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar esta máquina")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(maquina, campo, valor)

    db.commit()
    db.refresh(maquina)
    return maquina


@router.delete("/{maquina_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_maquina(
    maquina_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    if maquina.propietario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta máquina")

    db.delete(maquina)
    db.commit()


@router.get("/{maquina_id}/disponibilidad", response_model=list[BloqueDisponibilidad])
def listar_disponibilidad_maquina(
    maquina_id: int,
    db: Session = Depends(get_db),
):
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")

    bloques: list[BloqueDisponibilidad] = []

    cotizaciones_aceptadas = (
        db.query(Cotizacion)
        .filter(
            Cotizacion.maquina_id == maquina_id,
            Cotizacion.estado == "aceptada",
        )
        .all()
    )
    for cot in cotizaciones_aceptadas:
        fi = cot.fecha_inicio_contraoferta or cot.fecha_inicio
        ff = cot.fecha_fin_contraoferta or cot.fecha_fin
        bloques.append(BloqueDisponibilidad(fecha_inicio=fi, fecha_fin=ff, motivo="Alquiler confirmado"))

    disponibilidad_manual = (
        db.query(Disponibilidad)
        .filter(Disponibilidad.maquina_id == maquina_id)
        .all()
    )
    for d in disponibilidad_manual:
        bloques.append(BloqueDisponibilidad(fecha_inicio=d.fecha_inicio, fecha_fin=d.fecha_fin, motivo=d.motivo or "No disponible"))

    bloques.sort(key=lambda b: b.fecha_inicio)
    return bloques
