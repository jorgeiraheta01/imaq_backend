from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth import (
    crear_access_token,
    crear_refresh_token,
    crear_reset_password_token,
    decodificar_token,
    hashear_password,
    obtener_usuario_actual,
    verificar_password,
)
from app.database import get_db
from app.email_utils import enviar_email_recuperacion
from app.models.sesion import Sesion
from app.models.usuario import Usuario
from app.rate_limit import limiter
from app.schemas.auth import (
    LoginRequest,
    RecuperarPasswordRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    Token,
)
from app.schemas.usuario import CambiarPasswordRequest, UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Marker stored in sesiones.dispositivo for password-reset tokens, so they
# can be distinguished from regular login refresh-token sessions.
MOTIVO_RESET_PASSWORD = "reset_password"


@router.post("/registro", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def registrar_usuario(request: Request, usuario: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == usuario.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    if db.query(Usuario).filter(Usuario.dui == usuario.dui).first():
        raise HTTPException(status_code=409, detail="Ya existe una cuenta con este DUI.")

    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        telefono=usuario.telefono,
        rol=usuario.rol,
        dui=usuario.dui,
        password_hash=hashear_password(usuario.password),
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, credenciales: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == credenciales.email).first()
    if not usuario or not verificar_password(credenciales.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = crear_access_token(data={"sub": usuario.email})
    refresh_token, expira_en = crear_refresh_token(data={"sub": usuario.email})

    db.add(
        Sesion(
            usuario_id=usuario.id,
            token=refresh_token,
            dispositivo=None,
            expira_en=expira_en.replace(tzinfo=None),
        )
    )
    db.commit()

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
@limiter.limit("100/minute")
def refrescar_token(request: Request, datos: RefreshTokenRequest, db: Session = Depends(get_db)):
    credenciales_invalidas = HTTPException(status_code=401, detail="Refresh token inválido o expirado")

    payload = decodificar_token(datos.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise credenciales_invalidas

    email = payload.get("sub")
    if not email:
        raise credenciales_invalidas

    sesion = (
        db.query(Sesion)
        .filter(Sesion.token == datos.refresh_token, Sesion.activo.is_(True))
        .first()
    )
    if not sesion or sesion.expira_en < datetime.now(timezone.utc).replace(tzinfo=None):
        raise credenciales_invalidas

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise credenciales_invalidas

    nuevo_access_token = crear_access_token(data={"sub": usuario.email})
    return Token(access_token=nuevo_access_token, refresh_token=datos.refresh_token)


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


@router.post("/recuperar-password", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def recuperar_password(request: Request, datos: RecuperarPasswordRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == datos.email).first()

    # Always return the same generic response whether or not the email
    # exists, so this endpoint can't be used to enumerate registered emails.
    if usuario:
        token, expira_en = crear_reset_password_token(data={"sub": usuario.email})
        db.add(
            Sesion(
                usuario_id=usuario.id,
                token=token,
                dispositivo=MOTIVO_RESET_PASSWORD,
                expira_en=expira_en.replace(tzinfo=None),
            )
        )
        db.commit()
        enviar_email_recuperacion(usuario.email, usuario.nombre, token)

    return {"detail": "Si el email existe, se ha enviado un enlace de recuperación."}


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
def reset_password(request: Request, datos: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_invalido = HTTPException(status_code=400, detail="Token inválido o expirado")

    payload = decodificar_token(datos.token)
    if not payload or payload.get("type") != "reset_password":
        raise token_invalido

    email = payload.get("sub")
    if not email:
        raise token_invalido

    sesion = (
        db.query(Sesion)
        .filter(
            Sesion.token == datos.token,
            Sesion.dispositivo == MOTIVO_RESET_PASSWORD,
            Sesion.activo.is_(True),
        )
        .first()
    )
    if not sesion or sesion.expira_en < datetime.now(timezone.utc).replace(tzinfo=None):
        raise token_invalido

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise token_invalido

    usuario.password_hash = hashear_password(datos.nueva_password)
    sesion.activo = False
    db.commit()
