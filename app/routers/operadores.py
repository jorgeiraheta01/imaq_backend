from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.operador import Operador
from app.models.usuario import Usuario
from app.schemas.schemas import OperadorCreate, OperadorOut, OperadorUpdate

router = APIRouter(prefix="/operadores", tags=["Operadores"])


@router.get("/", response_model=list[OperadorOut])
def listar_operadores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Operador).offset(skip).limit(limit).all()


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
    existente = db.query(Operador).filter(Operador.email == operador.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado para un operador")

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
