# iMaq Backend

API REST para **iMaq**, un marketplace de alquiler de maquinaria de construcción. Permite a proveedores publicar maquinaria, a clientes alquilarla, y opcionalmente contratar operadores.

## Stack

- **FastAPI** — framework web
- **SQLAlchemy** — ORM
- **PostgreSQL** — base de datos
- **Alembic** — migraciones de base de datos
- **JWT** (python-jose) — autenticación
- **Passlib (bcrypt)** — hash de contraseñas

## Estructura del proyecto

```
imaq_backend/
├── app/
│   ├── main.py            # punto de entrada de la app FastAPI
│   ├── database.py        # configuración de SQLAlchemy y sesión de BD
│   ├── auth.py             # utilidades de JWT y hashing de contraseñas
│   ├── models/             # modelos de SQLAlchemy (tablas)
│   ├── routers/            # endpoints agrupados por recurso
│   └── schemas/             # esquemas Pydantic (request/response)
├── alembic/                # migraciones de base de datos
├── requirements.txt
├── .env.example
└── README.md
```

## Configuración

1. Crea un entorno virtual e instala las dependencias:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copia `.env.example` a `.env` y completa los valores:

   ```bash
   copy .env.example .env
   ```

   Variables requeridas:
   - `DATABASE_URL`: cadena de conexión a PostgreSQL.
   - `SECRET_KEY`: clave secreta usada para firmar los tokens JWT.
   - `ALGORITHM` (opcional, default `HS256`).
   - `ACCESS_TOKEN_EXPIRE_MINUTES` (opcional, default `60`).

3. Crea la base de datos en PostgreSQL y aplica las migraciones:

   ```bash
   alembic upgrade head
   ```

4. Levanta el servidor de desarrollo:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Documentación interactiva disponible en `http://localhost:8000/docs`.

## Migraciones

- Generar una nueva migración a partir de cambios en los modelos:

  ```bash
  alembic revision --autogenerate -m "descripcion del cambio"
  ```

- Aplicar migraciones pendientes:

  ```bash
  alembic upgrade head
  ```

## Recursos principales

| Recurso     | Endpoints base       |
|-------------|-----------------------|
| Auth        | `/auth/registro`, `/auth/login` |
| Máquinas    | `/maquinas` |
| Operadores  | `/operadores` |
| Alquileres  | `/alquileres` |
