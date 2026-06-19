from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.foto_maquina import FotoMaquina
from app.models.maquina import Maquina
from app.models.usuario import Usuario
from app.schemas.foto_maquina import FotoMaquinaCreate, FotoMaquinaOut, FotoMaquinaUpdate

router = APIRouter(prefix="/fotos-maquinas", tags=["Fotos de máquinas"])


def _obtener_maquina_propia(maquina_id: int, usuario_actual: Usuario, db: Session) -> Maquina:
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")
    if maquina.propietario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No tienes permiso sobre esta máquina")
    return maquina


@router.get("/", response_model=list[FotoMaquinaOut])
def listar_fotos(
    maquina_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(FotoMaquina)
    if maquina_id is not None:
        query = query.filter(FotoMaquina.maquina_id == maquina_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{foto_id}", response_model=FotoMaquinaOut)
def obtener_foto(foto_id: int, db: Session = Depends(get_db)):
    foto = db.query(FotoMaquina).filter(FotoMaquina.id == foto_id).first()
    if not foto:
        raise HTTPException(status_code=404, detail="Foto no encontrada")
    return foto


@router.post("/", response_model=FotoMaquinaOut, status_code=status.HTTP_201_CREATED)
def crear_foto(
    foto: FotoMaquinaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _obtener_maquina_propia(foto.maquina_id, usuario_actual, db)

    nueva_foto = FotoMaquina(**foto.model_dump())
    db.add(nueva_foto)
    db.commit()
    db.refresh(nueva_foto)
    return nueva_foto


@router.put("/{foto_id}", response_model=FotoMaquinaOut)
def actualizar_foto(
    foto_id: int,
    datos: FotoMaquinaUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    foto = db.query(FotoMaquina).filter(FotoMaquina.id == foto_id).first()
    if not foto:
        raise HTTPException(status_code=404, detail="Foto no encontrada")
    _obtener_maquina_propia(foto.maquina_id, usuario_actual, db)

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(foto, campo, valor)

    db.commit()
    db.refresh(foto)
    return foto


@router.delete("/{foto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_foto(
    foto_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    foto = db.query(FotoMaquina).filter(FotoMaquina.id == foto_id).first()
    if not foto:
        raise HTTPException(status_code=404, detail="Foto no encontrada")
    _obtener_maquina_propia(foto.maquina_id, usuario_actual, db)

    db.delete(foto)
    db.commit()
