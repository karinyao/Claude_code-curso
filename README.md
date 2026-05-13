# Todo API — Backend (Parte 1)

REST API construida con **Python · FastAPI · SQLite** (sin ORM). Cubre los cinco endpoints CRUD con validación Pydantic, manejo de errores y 23 tests automatizados.

---

## Estructura del proyecto

```
todo-app/
├── app/
│   ├── __init__.py
│   ├── main.py        # App factory (lifespan, CORS, router)
│   ├── database.py    # Conexión SQLite e init_db()
│   ├── models.py      # Modelos Pydantic (request / response)
│   ├── crud.py        # Operaciones de base de datos
│   └── routes.py      # Los 5 endpoints REST
├── tests/
│   ├── __init__.py
│   └── test_api.py    # 23 tests con base de datos aislada por test
├── requirements.txt
└── README.md
```

---

## Setup rápido

```bash
# 1. Clonar / copiar la carpeta todo-app
cd todo-app

# 2. Crear entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Levantar el servidor
uvicorn app.main:app --reload
# → http://localhost:8000
```

La base de datos `todos.db` se crea automáticamente en el primer arranque.

---

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/todos` | Lista todas las tareas. Acepta `?status=pending` o `?status=done` |
| `GET` | `/api/todos/{id}` | Detalle de una tarea |
| `POST` | `/api/todos` | Crea una tarea nueva |
| `PATCH` | `/api/todos/{id}` | Actualiza título, descripción y/o estado |
| `DELETE` | `/api/todos/{id}` | Elimina una tarea |

### Documentación interactiva

Con el servidor corriendo, visita:
- **Swagger UI** → http://localhost:8000/docs
- **ReDoc** → http://localhost:8000/redoc

### Ejemplos rápidos

```bash
# Crear una tarea
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Comprar leche", "description": "Entera, 2 litros"}'

# Listar todas
curl http://localhost:8000/api/todos

# Filtrar por estado
curl "http://localhost:8000/api/todos?status=pending"

# Marcar como hecha
curl -X PATCH http://localhost:8000/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'

# Eliminar
curl -X DELETE http://localhost:8000/api/todos/1
```

---

## Tests

```bash
python -m pytest tests/ -v
```

Cada test corre contra una base de datos SQLite temporal (en `tmp_path` de pytest) — completamente aislada, sin tocar `todos.db`.

```
23 passed in 1.10s
```

**Cobertura por endpoint:**

| Endpoint | Tests |
|----------|-------|
| `GET /api/todos` | 5 (lista vacía, creadas, filtro pending, filtro done, filtro inválido) |
| `GET /api/todos/{id}` | 3 (existente, 404, campos de respuesta) |
| `POST /api/todos` | 5 (completa, solo título, sin título, título vacío, título muy largo) |
| `PATCH /api/todos/{id}` | 6 (título, estado, múltiples campos, 404, estado inválido, campo desconocido) |
| `DELETE /api/todos/{id}` | 4 (exitoso, verificar borrado, 404, conteo) |

---

## Decisiones de diseño

- **Sin ORM** — `sqlite3` estándar con `row_factory = sqlite3.Row` para acceso tipo dict.
- **Inyección de `db_path` vía `app.state`** — permite pasar una DB diferente en tests sin monkeypatching de módulos.
- **`PATCH` semántico** — solo actualiza los campos explícitamente enviados (`model_dump(exclude_none=True)`).
- **`model_config = {"extra": "forbid"}`** en `TodoUpdate` — rechaza campos desconocidos con 422.
- **CORS abierto** — `allow_origins=["*"]` para desarrollo local. Restringir en producción.
