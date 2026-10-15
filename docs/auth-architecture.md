# Arquitectura del módulo de autenticación (MVC)

Stack: FastAPI + SQLAlchemy + Jinja2 + HTMX (definido en [CLAUDE.md](../CLAUDE.md)).
Mapeo de responsabilidades al patrón MVC clásico:

| MVC | Carpeta | Contenido |
|---|---|---|
| **Model** | `app/models/user.py` | Entidad `User` (SQLAlchemy): id, email, password_hash, role, created_at |
| **Model** | `app/repositories/user_repository.py` | Acceso a datos: `get_by_email`, `create`, `exists_by_email` |
| **Controller** | `app/routers/auth.py` | Endpoints FastAPI: `GET/POST /auth/register`, `GET/POST /auth/login`, `POST /auth/logout` |
| **Controller (lógica)** | `app/services/auth_service.py` | Reglas de negocio: hash/verificación de password (`pwdlib`), creación de sesión firmada (`itsdangerous`) |
| **View** | `templates/auth/login.html`, `templates/auth/register.html` | Formularios completos (extienden `base.html`) |
| **View (parcial HTMX)** | `templates/auth/_error.html` | Fragmento de error reenviado por `hx-post` sin recargar la página |

## Flujo de una petición (login)

```
Browser (form hx-post="/auth/login")
   → Controller: routers/auth.py::login_submit
        → Service: auth_service.authenticate(email, password)
             → Repository: user_repository.get_by_email
                  → Model/SQLAlchemy → MySQL
        ← Service crea cookie de sesión firmada (itsdangerous)
   ← Controller devuelve:
        - éxito: redirect (HX-Redirect header) a /
        - error: fragmento templates/auth/_error.html (200, re-renderiza el div del form)
```

## Sesión y control de acceso

- Sesión = cookie firmada con `itsdangerous` (no JWT, no tabla de sesiones): guarda `user_id` y `role`.
- Dependencia `app/dependencies/auth.py::get_current_user` lee y valida la cookie en cada request protegida.
- Dependencia `require_role(*roles)` reutiliza `get_current_user` y lanza `403` si el rol no está permitido.
- El control de acceso vive en las dependencias del **Controller**, nunca en el template: la View solo oculta botones que el usuario no podría usar, pero el backend siempre re-valida.

## Por qué no hay capa extra

- Un solo `auth_service.py`, no interfaces/abstract classes: solo hay una implementación (`ponytail`: YAGNI).
- No hay tabla `sessions`: la cookie firmada evita esa entidad y su limpieza.
- No hay JWT/OAuth: la app es tradicional basada en sesión de servidor, como indica CLAUDE.md.

## Test de humo

`tests/test_auth.py` (httpx + pytest-asyncio): registro → login exitoso → login con password incorrecta (401) → acceso a ruta protegida sin sesión (401/redirect).
