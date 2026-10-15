# Biblioteca Villa de los Estudiantes

Sistema de gestión de biblioteca para una escuela rural: catálogo de libros,
lectores, préstamos, devoluciones con multas, reservas y reportes.

Construido con FastAPI + SQLAlchemy + Jinja2 + HTMX sobre MySQL (SQLite en
memoria para las pruebas). El enfoque del proyecto es académico, orientado a
pruebas de software (ver `docs/`).

## Requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Un servidor MySQL accesible (o ajustar `DATABASE_URL` en `.env`)

## Instalación

```bash
uv sync --all-groups
cp .env.example .env  # ajustar DATABASE_URL y SECRET_KEY
```

## Ejecutar la aplicación

```bash
uv run uvicorn main:app --reload
```

La aplicación crea las tablas automáticamente al iniciar (no se usan
migraciones de Alembic en este proyecto). El primer usuario `LIBRARIAN` debe
sembrarse manualmente (no hay registro público de ese rol):

```bash
uv run python -c "
from app.database import SessionLocal
from app.services import auth_service
from app.models.user import UserRole

db = SessionLocal()
auth_service.register(db, name='Bibliotecario', email='biblioteca@villa.edu', password='cambia-esto', role=UserRole.LIBRARIAN)
"
```

## Roles

- **LIBRARIAN**: gestiona libros, inventario, préstamos, devoluciones, lectores y reportes.
- **STUDENT** / **COMMUNITY**: buscan libros, consultan disponibilidad, reservan y consultan sus propios préstamos/reservas.

## Pruebas

```bash
uv run ruff check .
uv run pytest --cov=app --cov-report=term-missing
```

Las pruebas están organizadas como una pirámide (`tests/unit`,
`tests/integration`, `tests/e2e`), con un comentario de trazabilidad al
requisito funcional (`# RF-0x`) al inicio de cada archivo. El pipeline de
GitLab CI (`.gitlab-ci.yml`) exige cobertura ≥80% en `app/services`.

## Documentación

- [`docs/auth-architecture.md`](docs/auth-architecture.md): diseño de autenticación y sesiones.
