from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.dispositivo import Dispositivo
from app.models.usuario import Usuario
from app.schemas.dispositivo import DispositivoCreate, DispositivoOut, DispositivoUpdate

router = APIRouter(prefix="/dispositivos", tags=["Dispositivos"])


@router.get("/", response_model=list[DispositivoOut])
def listar_dispositivos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    return (
        db.query(Dispositivo)
        .filter(Dispositivo.usuario_id == usuario_actual.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{dispositivo_id}", response_model=DispositivoOut)
def obtener_dispositivo(
    dispositivo_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    if dispositivo.usuario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este dispositivo")
    return dispositivo


@router.post("/", response_model=DispositivoOut, status_code=status.HTTP_201_CREATED)
def crear_dispositivo(
    dispositivo: DispositivoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    nuevo_dispositivo = Dispositivo(**dispositivo.model_dump(), usuario_id=usuario_actual.id)
    db.add(nuevo_dispositivo)
    db.commit()
    db.refresh(nuevo_dispositivo)
    return nuevo_dispositivo


@router.put("/{dispositivo_id}", response_model=DispositivoOut)
def actualizar_dispositivo(
    dispositivo_id: int,
    datos: DispositivoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    if dispositivo.usuario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este dispositivo")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(dispositivo, campo, valor)

    db.commit()
    db.refresh(dispositivo)
    return dispositivo


@router.delete("/{dispositivo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_dispositivo(
    dispositivo_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    if dispositivo.usuario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este dispositivo")

    db.delete(dispositivo)
    db.commit()
