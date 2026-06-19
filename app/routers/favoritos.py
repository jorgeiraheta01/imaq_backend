from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.favorito import Favorito
from app.models.maquina import Maquina
from app.models.usuario import Usuario
from app.schemas.favorito import FavoritoCreate, FavoritoOut

router = APIRouter(prefix="/favoritos", tags=["Favoritos"])


@router.get("/", response_model=list[FavoritoOut])
def listar_favoritos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    return (
        db.query(Favorito)
        .filter(Favorito.usuario_id == usuario_actual.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{favorito_id}", response_model=FavoritoOut)
def obtener_favorito(
    favorito_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    favorito = db.query(Favorito).filter(Favorito.id == favorito_id).first()
    if not favorito:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")
    if favorito.usuario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este favorito")
    return favorito


@router.post("/", response_model=FavoritoOut, status_code=status.HTTP_201_CREATED)
def crear_favorito(
    favorito: FavoritoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    maquina = db.query(Maquina).filter(Maquina.id == favorito.maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")

    existente = (
        db.query(Favorito)
        .filter(Favorito.usuario_id == usuario_actual.id, Favorito.maquina_id == favorito.maquina_id)
        .first()
    )
    if existente:
        raise HTTPException(status_code=400, detail="Esta máquina ya está en tus favoritos")

    nuevo_favorito = Favorito(**favorito.model_dump(), usuario_id=usuario_actual.id)
    db.add(nuevo_favorito)
    db.commit()
    db.refresh(nuevo_favorito)
    return nuevo_favorito


@router.delete("/{favorito_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_favorito(
    favorito_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    favorito = db.query(Favorito).filter(Favorito.id == favorito_id).first()
    if not favorito:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")
    if favorito.usuario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este favorito")

    db.delete(favorito)
    db.commit()
