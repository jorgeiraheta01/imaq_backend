from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.documento_verificacion import DocumentoVerificacion
from app.models.usuario import Usuario
from app.schemas.documento_verificacion import DocumentoVerificacionCreate, DocumentoVerificacionOut

router = APIRouter(prefix="/documentos-verificacion", tags=["Documentos de verificación"])


@router.get("/", response_model=list[DocumentoVerificacionOut])
def listar_documentos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    return (
        db.query(DocumentoVerificacion)
        .filter(DocumentoVerificacion.usuario_id == usuario_actual.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", response_model=DocumentoVerificacionOut, status_code=status.HTTP_201_CREATED)
def crear_documento(
    documento: DocumentoVerificacionCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    nuevo_documento = DocumentoVerificacion(
        **documento.model_dump(exclude={"usuario_id"}), usuario_id=usuario_actual.id
    )
    db.add(nuevo_documento)
    db.commit()
    db.refresh(nuevo_documento)
    return nuevo_documento
