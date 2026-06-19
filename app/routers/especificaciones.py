from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.especificacion import Especificacion
from app.models.maquina import Maquina
from app.models.usuario import Usuario
from app.schemas.especificacion import EspecificacionCreate, EspecificacionOut, EspecificacionUpdate

router = APIRouter(prefix="/especificaciones", tags=["Especificaciones"])


def _obtener_maquina_propia(maquina_id: int, usuario_actual: Usuario, db: Session) -> Maquina:
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    if maquina.propietario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso sobre esta máquina")
    return maquina


@router.get("/", response_model=list[EspecificacionOut])
def listar_especificaciones(
    maquina_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Especificacion)
    if maquina_id is not None:
        query = query.filter(Especificacion.maquina_id == maquina_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{especificacion_id}", response_model=EspecificacionOut)
def obtener_especificacion(especificacion_id: int, db: Session = Depends(get_db)):
    especificacion = db.query(Especificacion).filter(Especificacion.id == especificacion_id).first()
    if not especificacion:
        raise HTTPException(status_code=404, detail="Especificación no encontrada")
    return especificacion


@router.post("/", response_model=EspecificacionOut, status_code=status.HTTP_201_CREATED)
def crear_especificacion(
    especificacion: EspecificacionCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _obtener_maquina_propia(especificacion.maquina_id, usuario_actual, db)

    nueva_especificacion = Especificacion(**especificacion.model_dump())
    db.add(nueva_especificacion)
    db.commit()
    db.refresh(nueva_especificacion)
    return nueva_especificacion


@router.put("/{especificacion_id}", response_model=EspecificacionOut)
def actualizar_especificacion(
    especificacion_id: int,
    datos: EspecificacionUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    especificacion = db.query(Especificacion).filter(Especificacion.id == especificacion_id).first()
    if not especificacion:
        raise HTTPException(status_code=404, detail="Especificación no encontrada")
    _obtener_maquina_propia(especificacion.maquina_id, usuario_actual, db)

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(especificacion, campo, valor)

    db.commit()
    db.refresh(especificacion)
    return especificacion


@router.delete("/{especificacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_especificacion(
    especificacion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    especificacion = db.query(Especificacion).filter(Especificacion.id == especificacion_id).first()
    if not especificacion:
        raise HTTPException(status_code=404, detail="Especificación no encontrada")
    _obtener_maquina_propia(especificacion.maquina_id, usuario_actual, db)

    db.delete(especificacion)
    db.commit()
