from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models.user import User, UserRole
from app.services import reservation_service
from app.templates import templates

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("/mine", response_class=HTMLResponse)
def mine(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reservations = reservation_service.list_my_reservations(db, user)
    return templates.TemplateResponse(
        request, "reservations/mine.html", {"reservations": reservations, "user": user}
    )


@router.post("", response_class=HTMLResponse)
def create(
    request: Request,
    book_id: int = Form(...),
    user: User = Depends(require_role(UserRole.STUDENT, UserRole.COMMUNITY)),
    db: Session = Depends(get_db),
):
    try:
        reservation_service.create_reservation(db, user=user, book_id=book_id)
    except reservation_service.ReservationError as exc:
        return templates.TemplateResponse(
            request, "reservations/_error.html", {"message": str(exc)}
        )
    reservations = reservation_service.list_my_reservations(db, user)
    return templates.TemplateResponse(
        request, "reservations/_rows.html", {"reservations": reservations}
    )
