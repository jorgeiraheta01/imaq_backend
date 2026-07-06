import json
import logging
import os
import time
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler

import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text

from app.auth import ALGORITHM, SECRET_KEY
from app.database import get_db
from app.rate_limit import limiter
from app.routers import (
    alquileres,
    auth,
    calificaciones,
    cotizaciones,
    departamentos,
    disponibilidad,
    documentos_verificacion,
    dispositivos,
    especificaciones,
    favoritos,
    fotos_maquinas,
    maquinas,
    operadores,
    sesiones,
    usuarios,
)
from jose import JWTError, jwt

load_dotenv()

# ───────────────────────── SENTRY ─────────────────────────
# Silently skipped if SENTRY_DSN isn't set (e.g. local development).
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0, send_default_pii=False)

# ───────────────────────── STRUCTURED LOGGING ─────────────────────────
os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("imaq")
logger.setLevel(logging.INFO)
_handler = TimedRotatingFileHandler("logs/imaq.log", when="midnight", backupCount=7, encoding="utf-8")
_handler.setFormatter(logging.Formatter("%(message)s"))
if not logger.handlers:
    logger.addHandler(_handler)

app = FastAPI(
    title="iMaq API",
    description="Marketplace de alquiler de maquinaria de construcción",
    version="1.0.0",
)

# ───────────────────────── RATE LIMITING ─────────────────────────
app.state.limiter = limiter


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiadas solicitudes. Intenta de nuevo en un momento."},
    )


app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)

# ───────────────────────── CORS ─────────────────────────
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ───────────────────────── SECURITY HEADERS ─────────────────────────
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# ───────────────────────── REQUEST LOGGING ─────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)

    usuario = None
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            usuario = payload.get("sub")
        except JWTError:
            pass

    logger.info(
        json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": request.method,
                "endpoint": request.url.path,
                "ip": request.client.host if request.client else None,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "usuario": usuario,
            },
            ensure_ascii=False,
        )
    )
    return response


app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(maquinas.router)
app.include_router(operadores.router)
app.include_router(alquileres.router)
app.include_router(departamentos.router)
app.include_router(fotos_maquinas.router)
app.include_router(especificaciones.router)
app.include_router(disponibilidad.router)
app.include_router(calificaciones.router)
app.include_router(favoritos.router)
app.include_router(dispositivos.router)
app.include_router(sesiones.router)
app.include_router(documentos_verificacion.router)
app.include_router(cotizaciones.router)


@app.get("/")
def root():
    return {"mensaje": "Bienvenido a la API de iMaq"}


@app.get("/health")
def health_check():
    db = next(get_db())
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    finally:
        db.close()

    return {
        "status": "ok",
        "version": "1.0.0",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
