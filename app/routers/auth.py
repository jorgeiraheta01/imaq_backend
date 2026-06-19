from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import crear_access_token, hashear_password, verificar_password
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, Token
from app.schemas.usuario import UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        telefono=usuario.telefono,
        rol=usuario.rol,
        password_hash=hashear_password(usuario.password),
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/login", response_model=Token)
def login(credenciales: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == credenciales.email).first()
    if not usuario or not verificar_password(credenciales.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = crear_access_token(data={"sub": usuario.email})
    return Token(access_token=access_token)
