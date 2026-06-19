from fastapi import FastAPI

from app.routers import alquileres, auth, maquinas, operadores

app = FastAPI(
    title="iMaq API",
    description="Marketplace de alquiler de maquinaria de construcción",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(maquinas.router)
app.include_router(operadores.router)
app.include_router(alquileres.router)


@app.get("/")
def root():
    return {"mensaje": "Bienvenido a la API de iMaq"}
