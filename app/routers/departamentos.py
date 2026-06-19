from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import obtener_usuario_actual
from app.database import get_db
from app.models.departamento import Departamento
from app.models.usuario import Usuario
from app.schemas.departamento import DepartamentoCreate, DepartamentoOut, DepartamentoUpdate

router = APIRouter(prefix="/departamentos", tags=["Departamentos"])


def _requerir_admin(usuario_actual: Usuario) -> None:
    if usuario_actual.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo un administrador puede realizar esta acción")


@router.get("/", response_model=list[DepartamentoOut])
def listar_departamentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Departamento).offset(skip).limit(limit).all()


@router.get("/{departamento_id}", response_model=DepartamentoOut)
def obtener_departamento(departamento_id: int, db: Session = Depends(get_db)):
    departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return departamento


@router.post("/", response_model=DepartamentoOut, status_code=status.HTTP_201_CREATED)
def crear_departamento(
    departamento: DepartamentoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _requerir_admin(usuario_actual)

    nuevo_departamento = Departamento(**departamento.model_dump())
    db.add(nuevo_departamento)
    db.commit()
    db.refresh(nuevo_departamento)
    return nuevo_departamento


@router.put("/{departamento_id}", response_model=DepartamentoOut)
def actualizar_departamento(
    departamento_id: int,
    datos: DepartamentoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _requerir_admin(usuario_actual)

    departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(departamento, campo, valor)

    db.commit()
    db.refresh(departamento)
    return departamento


@router.delete("/{departamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_departamento(
    departamento_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _requerir_admin(usuario_actual)

    departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")

    db.delete(departamento)
    db.commit()
