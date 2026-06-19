from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioPublicoOut

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/{usuario_id}", response_model=UsuarioPublicoOut)
def obtener_usuario_publico(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario
