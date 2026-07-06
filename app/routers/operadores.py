from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.operador import Operador
from app.models.usuario import Usuario
from app.schemas.operador import OperadorCreate, OperadorOut, OperadorUpdate

router = APIRouter(prefix="/operadores", tags=["Operadores"])

OrdenOperador = Literal["tarifa_asc", "tarifa_desc", "mejor_calificacion"]


@router.get("/", response_model=list[OperadorOut])
def listar_operadores(
    skip: int = 0,
    limit: int = 100,
    buscar: str | None = None,
    departamento_id: int | None = None,  # noqa: ARG001 — accepted but unused, see note below
    tarifa_max: float | None = None,
    verificado: bool | None = None,
    maquina: str | None = None,
    orden: OrdenOperador | None = None,
    db: Session = Depends(get_db),
):
    # departamento_id is accepted for API symmetry with /maquinas but currently
    # has no effect: neither Operador nor Usuario stores a department/location,
    # so there's nothing to filter on yet.
    query = db.query(Operador).join(Usuario, Operador.usuario_id == Usuario.id)

    if buscar:
        patron = f"%{buscar}%"
        query = query.filter(or_(Usuario.nombre.ilike(patron), Operador.certificaciones.ilike(patron)))
    if maquina:
        query = query.filter(Operador.certificaciones.ilike(f"%{maquina}%"))
    if tarifa_max is not None:
        query = query.filter(Operador.tarifa_dia <= tarifa_max)
    if verificado is not None:
        query = query.filter(Operador.verificado == verificado)

    if orden == "tarifa_asc":
        query = query.order_by(Operador.tarifa_dia.asc())
    elif orden == "tarifa_desc":
        query = query.order_by(Operador.tarifa_dia.desc())
    elif orden == "mejor_calificacion":
        # No rating is stored directly on Operador (calificaciones references
        # maquina/alquiler/usuario, not operador), so this falls back to a
        # reasonable quality proxy: verified first, then more experience.
        query = query.order_by(Operador.verificado.desc(), Operador.experiencia_anios.desc())

    return query.offset(skip).limit(limit).all()


@router.get("/count")
def contar_operadores(db: Session = Depends(get_db)):
    total = db.query(func.count(Operador.id)).scalar()
    return {"total": total}


@router.get("/{operador_id}", response_model=OperadorOut)
def obtener_operador(operador_id: int, db: Session = Depends(get_db)):
    operador = db.query(Operador).filter(Operador.id == operador_id).first()
    if not operador:
        raise HTTPException(status_code=404, detail="Operador no encontrado")
    return operador


@router.post("/", response_model=OperadorOut, status_code=status.HTTP_201_CREATED)
def crear_operador(
    operador: OperadorCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    existente = db.query(Operador).filter(Operador.usuario_id == operador.usuario_id).first()
    if existente:
        raise HTTPException(status_code=400, detail="Este usuario ya está registrado como operador")

    nuevo_operador = Operador(**operador.model_dump())
    db.add(nuevo_operador)
    db.commit()
    db.refresh(nuevo_operador)
    return nuevo_operador


@router.put("/{operador_id}", response_model=OperadorOut)
def actualizar_operador(
    operador_id: int,
    datos: OperadorUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    operador = db.query(Operador).filter(Operador.id == operador_id).first()
    if not operador:
        raise HTTPException(status_code=404, detail="Operador no encontrado")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(operador, campo, valor)

    db.commit()
    db.refresh(operador)
    return operador


@router.delete("/{operador_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_operador(
    operador_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    operador = db.query(Operador).filter(Operador.id == operador_id).first()
    if not operador:
        raise HTTPException(status_code=404, detail="Operador no encontrado")

    db.delete(operador)
    db.commit()
