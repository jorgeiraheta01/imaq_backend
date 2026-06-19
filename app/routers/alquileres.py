from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.alquiler import Alquiler
from app.models.maquina import Maquina
from app.models.usuario import Usuario
from app.schemas.schemas import AlquilerCreate, AlquilerOut, AlquilerUpdate

router = APIRouter(prefix="/alquileres", tags=["Alquileres"])


@router.get("/", response_model=list[AlquilerOut])
def listar_alquileres(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    return (
        db.query(Alquiler)
        .filter(Alquiler.cliente_id == usuario_actual.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{alquiler_id}", response_model=AlquilerOut)
def obtener_alquiler(
    alquiler_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    alquiler = db.query(Alquiler).filter(Alquiler.id == alquiler_id).first()
    if not alquiler:
        raise HTTPException(status_code=404, detail="Alquiler no encontrado")
    if alquiler.cliente_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este alquiler")
    return alquiler


@router.post("/", response_model=AlquilerOut, status_code=status.HTTP_201_CREATED)
def crear_alquiler(
    alquiler: AlquilerCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    maquina = db.query(Maquina).filter(Maquina.id == alquiler.maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    if not maquina.disponible:
        raise HTTPException(status_code=400, detail="La máquina no está disponible")

    dias = (alquiler.fecha_fin - alquiler.fecha_inicio).days
    if dias <= 0:
        raise HTTPException(status_code=400, detail="El rango de fechas no es válido")

    costo_total = dias * maquina.precio_por_dia

    nuevo_alquiler = Alquiler(
        **alquiler.model_dump(),
        cliente_id=usuario_actual.id,
        costo_total=costo_total,
    )
    db.add(nuevo_alquiler)
    db.commit()
    db.refresh(nuevo_alquiler)
    return nuevo_alquiler


@router.put("/{alquiler_id}", response_model=AlquilerOut)
def actualizar_alquiler(
    alquiler_id: int,
    datos: AlquilerUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    alquiler = db.query(Alquiler).filter(Alquiler.id == alquiler_id).first()
    if not alquiler:
        raise HTTPException(status_code=404, detail="Alquiler no encontrado")
    if alquiler.cliente_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este alquiler")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(alquiler, campo, valor)

    db.commit()
    db.refresh(alquiler)
    return alquiler


@router.delete("/{alquiler_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_alquiler(
    alquiler_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    alquiler = db.query(Alquiler).filter(Alquiler.id == alquiler_id).first()
    if not alquiler:
        raise HTTPException(status_code=404, detail="Alquiler no encontrado")
    if alquiler.cliente_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para cancelar este alquiler")

    alquiler.estado = "cancelado"
    db.commit()
