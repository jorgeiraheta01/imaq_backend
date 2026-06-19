from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.disponibilidad import Disponibilidad
from app.models.maquina import Maquina
from app.models.usuario import Usuario
from app.schemas.disponibilidad import DisponibilidadCreate, DisponibilidadOut, DisponibilidadUpdate

router = APIRouter(prefix="/disponibilidad", tags=["Disponibilidad"])


def _obtener_maquina_propia(maquina_id: int, usuario_actual: Usuario, db: Session) -> Maquina:
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    if maquina.propietario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso sobre esta máquina")
    return maquina


@router.get("/", response_model=list[DisponibilidadOut])
def listar_disponibilidad(
    maquina_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Disponibilidad)
    if maquina_id is not None:
        query = query.filter(Disponibilidad.maquina_id == maquina_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{disponibilidad_id}", response_model=DisponibilidadOut)
def obtener_disponibilidad(disponibilidad_id: int, db: Session = Depends(get_db)):
    disponibilidad = db.query(Disponibilidad).filter(Disponibilidad.id == disponibilidad_id).first()
    if not disponibilidad:
        raise HTTPException(status_code=404, detail="Registro de disponibilidad no encontrado")
    return disponibilidad


@router.post("/", response_model=DisponibilidadOut, status_code=status.HTTP_201_CREATED)
def crear_disponibilidad(
    disponibilidad: DisponibilidadCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _obtener_maquina_propia(disponibilidad.maquina_id, usuario_actual, db)

    if disponibilidad.fecha_fin < disponibilidad.fecha_inicio:
        raise HTTPException(status_code=400, detail="El rango de fechas no es válido")

    nueva_disponibilidad = Disponibilidad(**disponibilidad.model_dump())
    db.add(nueva_disponibilidad)
    db.commit()
    db.refresh(nueva_disponibilidad)
    return nueva_disponibilidad


@router.put("/{disponibilidad_id}", response_model=DisponibilidadOut)
def actualizar_disponibilidad(
    disponibilidad_id: int,
    datos: DisponibilidadUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    disponibilidad = db.query(Disponibilidad).filter(Disponibilidad.id == disponibilidad_id).first()
    if not disponibilidad:
        raise HTTPException(status_code=404, detail="Registro de disponibilidad no encontrado")
    _obtener_maquina_propia(disponibilidad.maquina_id, usuario_actual, db)

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(disponibilidad, campo, valor)

    db.commit()
    db.refresh(disponibilidad)
    return disponibilidad


@router.delete("/{disponibilidad_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_disponibilidad(
    disponibilidad_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    disponibilidad = db.query(Disponibilidad).filter(Disponibilidad.id == disponibilidad_id).first()
    if not disponibilidad:
        raise HTTPException(status_code=404, detail="Registro de disponibilidad no encontrado")
    _obtener_maquina_propia(disponibilidad.maquina_id, usuario_actual, db)

    db.delete(disponibilidad)
    db.commit()
