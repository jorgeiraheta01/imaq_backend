from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.alquiler import Alquiler
from app.models.calificacion import Calificacion
from app.models.usuario import Usuario
from app.schemas.calificacion import CalificacionCreate, CalificacionOut, CalificacionUpdate

router = APIRouter(prefix="/calificaciones", tags=["Calificaciones"])


@router.get("/", response_model=list[CalificacionOut])
def listar_calificaciones(
    maquina_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Calificacion)
    if maquina_id is not None:
        query = query.filter(Calificacion.maquina_id == maquina_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{calificacion_id}", response_model=CalificacionOut)
def obtener_calificacion(calificacion_id: int, db: Session = Depends(get_db)):
    calificacion = db.query(Calificacion).filter(Calificacion.id == calificacion_id).first()
    if not calificacion:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")
    return calificacion


@router.post("/", response_model=CalificacionOut, status_code=status.HTTP_201_CREATED)
def crear_calificacion(
    calificacion: CalificacionCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    alquiler = db.query(Alquiler).filter(Alquiler.id == calificacion.alquiler_id).first()
    if not alquiler:
        raise HTTPException(status_code=404, detail="Alquiler no encontrado")
    if alquiler.arrendatario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No puedes calificar un alquiler que no es tuyo")
    if alquiler.estado != "finalizado":
        raise HTTPException(status_code=400, detail="Solo puedes calificar alquileres finalizados")
    if alquiler.maquina_id != calificacion.maquina_id:
        raise HTTPException(status_code=400, detail="La máquina no corresponde a este alquiler")

    nueva_calificacion = Calificacion(**calificacion.model_dump(), usuario_id=usuario_actual.id)
    db.add(nueva_calificacion)
    db.commit()
    db.refresh(nueva_calificacion)
    return nueva_calificacion


@router.put("/{calificacion_id}", response_model=CalificacionOut)
def actualizar_calificacion(
    calificacion_id: int,
    datos: CalificacionUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    calificacion = db.query(Calificacion).filter(Calificacion.id == calificacion_id).first()
    if not calificacion:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")
    if calificacion.usuario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar esta calificación")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(calificacion, campo, valor)

    db.commit()
    db.refresh(calificacion)
    return calificacion


@router.delete("/{calificacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_calificacion(
    calificacion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    calificacion = db.query(Calificacion).filter(Calificacion.id == calificacion_id).first()
    if not calificacion:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")
    if calificacion.usuario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta calificación")

    db.delete(calificacion)
    db.commit()
