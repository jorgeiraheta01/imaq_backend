from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import crear_access_token, hashear_password
from app.database import Base, get_db
from app.main import app
from app.models.alquiler import Alquiler
from app.models.maquina import Maquina
from app.models.usuario import Usuario

# Cada test corre contra una base SQLite en memoria propia (no la Postgres real
# de desarrollo), aislada por StaticPool para que la misma conexión persista
# durante todo el test aunque FastAPI abra varias "sesiones" por request.


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def crear_usuario(
    db_session,
    *,
    nombre: str,
    email: str,
    rol: str,
    password: str = "Password123!",
) -> Usuario:
    usuario = Usuario(
        nombre=nombre,
        email=email,
        password_hash=hashear_password(password),
        rol=rol,
        verificado=True,
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


def crear_maquina(db_session, *, propietario: Usuario, nombre: str = "Excavadora Test", precio_dia: str = "100.00") -> Maquina:
    maquina = Maquina(
        propietario_id=propietario.id,
        nombre=nombre,
        tipo="Excavadora",
        precio_dia=precio_dia,
        estado="disponible",
    )
    db_session.add(maquina)
    db_session.commit()
    db_session.refresh(maquina)
    return maquina


def crear_alquiler(
    db_session,
    *,
    maquina: Maquina,
    arrendatario: Usuario,
    fecha_inicio: date = date(2026, 1, 1),
    fecha_fin: date = date(2026, 1, 5),
    precio_acordado: str = "100.00",
    estado: str = "activo",
) -> Alquiler:
    alquiler = Alquiler(
        maquina_id=maquina.id,
        arrendatario_id=arrendatario.id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        precio_acordado=precio_acordado,
        costo_total=str(float(precio_acordado) * (fecha_fin - fecha_inicio).days),
        estado=estado,
    )
    db_session.add(alquiler)
    db_session.commit()
    db_session.refresh(alquiler)
    return alquiler


def auth_headers(usuario: Usuario) -> dict:
    token = crear_access_token(data={"sub": usuario.email})
    return {"Authorization": f"Bearer {token}"}
