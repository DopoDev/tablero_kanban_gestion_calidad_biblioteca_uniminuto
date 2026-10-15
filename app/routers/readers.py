from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_role
from app.models.user import User, UserRole
from app.services import user_service
from app.templates import templates

router = APIRouter(prefix="/readers", tags=["readers"])


@router.get("", response_class=HTMLResponse)
def index(
    request: Request,
    user: User = Depends(require_role(UserRole.LIBRARIAN)),
    db: Session = Depends(get_db),
):
    readers = user_service.list_readers(db)
    return templates.TemplateResponse(
        request, "readers/index.html", {"readers": readers, "user": user}
    )


@router.post("/{user_id}/suspend", response_class=HTMLResponse)
def suspend(
    request: Request,
    user_id: int,
    user: User = Depends(require_role(UserRole.LIBRARIAN)),
    db: Session = Depends(get_db),
):
    try:
        user_service.suspend_reader(db, user_id=user_id)
    except user_service.UserError as exc:
        return templates.TemplateResponse(request, "readers/_error.html", {"message": str(exc)})
    readers = user_service.list_readers(db)
    return templates.TemplateResponse(request, "readers/_rows.html", {"readers": readers})


@router.post("/{user_id}/activate", response_class=HTMLResponse)
def activate(
    request: Request,
    user_id: int,
    user: User = Depends(require_role(UserRole.LIBRARIAN)),
    db: Session = Depends(get_db),
):
    try:
        user_service.activate_reader(db, user_id=user_id)
    except user_service.UserError as exc:
        return templates.TemplateResponse(request, "readers/_error.html", {"message": str(exc)})
    readers = user_service.list_readers(db)
    return templates.TemplateResponse(request, "readers/_rows.html", {"readers": readers})


@router.post("/{user_id}/edit", response_class=HTMLResponse)
def edit_contact(
    request: Request,
    user_id: int,
    phone: str = Form(""),
    user: User = Depends(require_role(UserRole.LIBRARIAN)),
    db: Session = Depends(get_db),
):
    try:
        user_service.update_contact(db, user_id=user_id, phone=phone or None)
    except user_service.UserError as exc:
        return templates.TemplateResponse(request, "readers/_error.html", {"message": str(exc)})
    readers = user_service.list_readers(db)
    return templates.TemplateResponse(request, "readers/_rows.html", {"readers": readers})
