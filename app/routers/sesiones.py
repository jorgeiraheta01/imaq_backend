from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.sesion import Sesion
from app.models.usuario import Usuario
from app.schemas.sesion import SesionCreate, SesionOut

router = APIRouter(prefix="/sesiones", tags=["Sesiones"])


@router.get("/", response_model=list[SesionOut])
def listar_sesiones(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    return (
        db.query(Sesion)
        .filter(Sesion.usuario_id == usuario_actual.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", response_model=SesionOut, status_code=status.HTTP_201_CREATED)
def crear_sesion(
    sesion: SesionCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    nueva_sesion = Sesion(**sesion.model_dump(exclude={"usuario_id"}), usuario_id=usuario_actual.id)
    db.add(nueva_sesion)
    db.commit()
    db.refresh(nueva_sesion)
    return nueva_sesion


@router.delete("/todas", status_code=status.HTTP_204_NO_CONTENT)
def cerrar_todas_las_sesiones(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    db.query(Sesion).filter(Sesion.usuario_id == usuario_actual.id).update({"activo": False})
    db.commit()
