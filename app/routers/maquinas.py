from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.maquina import Maquina
from app.models.usuario import Usuario
from app.schemas.maquina import MaquinaCreate, MaquinaOut, MaquinaUpdate

router = APIRouter(prefix="/maquinas", tags=["Máquinas"])


@router.get("/", response_model=list[MaquinaOut])
def listar_maquinas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Maquina).offset(skip).limit(limit).all()


@router.get("/{maquina_id}", response_model=MaquinaOut)
def obtener_maquina(maquina_id: int, db: Session = Depends(get_db)):
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    return maquina


@router.post("/", response_model=MaquinaOut, status_code=status.HTTP_201_CREATED)
def crear_maquina(
    maquina: MaquinaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    nueva_maquina = Maquina(**maquina.model_dump(), propietario_id=usuario_actual.id)
    db.add(nueva_maquina)
    db.commit()
    db.refresh(nueva_maquina)
    return nueva_maquina


@router.put("/{maquina_id}", response_model=MaquinaOut)
def actualizar_maquina(
    maquina_id: int,
    datos: MaquinaUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    if maquina.propietario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar esta máquina")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(maquina, campo, valor)

    db.commit()
    db.refresh(maquina)
    return maquina


@router.delete("/{maquina_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_maquina(
    maquina_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    if maquina.propietario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta máquina")

    db.delete(maquina)
    db.commit()
