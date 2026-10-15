from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import UserRole
from app.services import auth_service
from app.templates import templates

router = APIRouter(prefix="/auth", tags=["auth"])

# ponytail: registro publico solo permite STUDENT/COMMUNITY; LIBRARIAN se crea manualmente (seed/DBA).
REGISTERABLE_ROLES = (UserRole.STUDENT, UserRole.COMMUNITY)


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse(request, "auth/register.html")


@router.post("/register", response_class=HTMLResponse)
def register_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: UserRole = Form(...),
    phone: str = Form(""),
    db: Session = Depends(get_db),
):
    if role not in REGISTERABLE_ROLES:
        return templates.TemplateResponse(
            request, "auth/_error.html", {"message": "Rol no permitido para registro."}
        )
    try:
        user = auth_service.register(
            db, name=name, email=email, password=password, role=role, phone=phone or None
        )
    except auth_service.AuthError as exc:
        return templates.TemplateResponse(request, "auth/_error.html", {"message": str(exc)})

    response = Response(status_code=200, headers={"HX-Redirect": "/"})
    response.set_cookie(
        auth_service.SESSION_COOKIE,
        auth_service.create_session_cookie(user),
        httponly=True,
        samesite="lax",
        max_age=auth_service.SESSION_MAX_AGE,
    )
    return response


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse(request, "auth/login.html")


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user = auth_service.authenticate(db, email=email, password=password)
    except auth_service.AuthError as exc:
        return templates.TemplateResponse(request, "auth/_error.html", {"message": str(exc)})

    response = Response(status_code=200, headers={"HX-Redirect": "/"})
    response.set_cookie(
        auth_service.SESSION_COOKIE,
        auth_service.create_session_cookie(user),
        httponly=True,
        samesite="lax",
        max_age=auth_service.SESSION_MAX_AGE,
    )
    return response


@router.post("/logout")
def logout():
    response = Response(status_code=200, headers={"HX-Redirect": "/auth/login"})
    response.delete_cookie(auth_service.SESSION_COOKIE)
    return response
