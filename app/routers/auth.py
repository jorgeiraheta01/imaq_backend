from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import crear_access_token, hashear_password, obtener_usuario_actual, verificar_password
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, Token
from app.schemas.usuario import CambiarPasswordRequest, UsuarioCreate, UsuarioOut

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


@router.get("/me", response_model=UsuarioOut)
def obtener_perfil_actual(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return usuario_actual


@router.put("/cambiar-password", status_code=status.HTTP_204_NO_CONTENT)
def cambiar_password(
    datos: CambiarPasswordRequest,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    if not verificar_password(datos.password_actual, usuario_actual.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")

    usuario_actual.password_hash = hashear_password(datos.password_nueva)
    db.commit()
