from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.alquiler import Alquiler
from app.models.maquina import Maquina
from app.models.usuario import Usuario
from app.schemas.alquiler import AlquilerCreate, AlquilerOut, AlquilerPublicoOut, AlquilerUpdate

router = APIRouter(prefix="/alquileres", tags=["Alquileres"])


@router.get("/", response_model=list[AlquilerOut])
def listar_alquileres(
    rol: Literal["arrendatario", "propietario", "todos"] = "arrendatario",
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """`rol` decide de qué lado de la relación se listan los alquileres:
    - arrendatario (default, preserva el comportamiento previo): donde el
      usuario alquiló una máquina de otro.
    - propietario: donde el usuario es dueño de la máquina alquilada.
    - todos: unión de ambos casos (útil para un usuario con ambos roles).
    """
    query = db.query(Alquiler)
    if rol == "arrendatario":
        query = query.filter(Alquiler.arrendatario_id == usuario_actual.id)
    elif rol == "propietario":
        query = query.join(Maquina, Alquiler.maquina_id == Maquina.id).filter(
            Maquina.propietario_id == usuario_actual.id
        )
    else:
        query = query.join(Maquina, Alquiler.maquina_id == Maquina.id).filter(
            or_(
                Alquiler.arrendatario_id == usuario_actual.id,
                Maquina.propietario_id == usuario_actual.id,
            )
        )
    return query.offset(skip).limit(limit).all()


@router.get("/publico/por-maquina/{maquina_id}", response_model=list[AlquilerPublicoOut])
def listar_alquileres_publicos_por_maquina(maquina_id: int, db: Session = Depends(get_db)):
    """Historial público de alquileres de una máquina (sin auth), para mostrar
    en el catálogo/modal de detalle. No expone arrendatario_id ni precios."""
    return (
        db.query(Alquiler)
        .filter(
            Alquiler.maquina_id == maquina_id,
            Alquiler.estado.in_(["activo", "finalizado"]),
        )
        .order_by(Alquiler.fecha_inicio.desc())
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
    if usuario_actual.id not in (alquiler.arrendatario_id, alquiler.propietario_id):
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
    if maquina.estado != "disponible":
        raise HTTPException(status_code=400, detail="La máquina no está disponible")

    dias = (alquiler.fecha_fin - alquiler.fecha_inicio).days
    if dias <= 0:
        raise HTTPException(status_code=400, detail="El rango de fechas no es válido")

    costo_total = dias * alquiler.precio_acordado

    nuevo_alquiler = Alquiler(
        **alquiler.model_dump(),
        arrendatario_id=usuario_actual.id,
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
    if alquiler.arrendatario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este alquiler")

    # estado y costo_total no son editables por el arrendatario: solo el flujo
    # de aceptacion de cotizacion o un proceso del sistema debe fijarlos.
    for campo, valor in datos.model_dump(exclude_unset=True, exclude={"estado", "costo_total"}).items():
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
    if alquiler.arrendatario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para cancelar este alquiler")

    alquiler.estado = "cancelado"
    db.commit()
