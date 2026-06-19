from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioOut, UsuarioPublicoOut, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/{usuario_id}", response_model=UsuarioPublicoOut)
def obtener_usuario_publico(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    if usuario_id != usuario_actual.id:
        raise HTTPException(status_code=403, detail="No puedes editar el perfil de otro usuario")

    for campo, valor in datos.model_dump(exclude_unset=True, exclude={"verificado"}).items():
        setattr(usuario_actual, campo, valor)

    db.commit()
    db.refresh(usuario_actual)
    return usuario_actual
