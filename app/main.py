from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    alquileres,
    auth,
    calificaciones,
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

app = FastAPI(
    title="iMaq API",
    description="Marketplace de alquiler de maquinaria de construcción",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/")
def root():
    return {"mensaje": "Bienvenido a la API de iMaq"}
