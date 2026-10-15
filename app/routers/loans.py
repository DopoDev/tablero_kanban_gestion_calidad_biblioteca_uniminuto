from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models.user import User, UserRole
from app.repositories import loan_repository, user_repository
from app.services import loan_service
from app.templates import templates

router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("", response_class=HTMLResponse)
def index(
    request: Request,
    user: User = Depends(require_role(UserRole.LIBRARIAN)),
    db: Session = Depends(get_db),
):
    loans = loan_repository.list_all(db)
    return templates.TemplateResponse(request, "loans/index.html", {"loans": loans, "user": user})


@router.get("/mine", response_class=HTMLResponse)
def mine(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    loans = loan_repository.list_active_for_user(db, user.id)
    return templates.TemplateResponse(request, "loans/mine.html", {"loans": loans, "user": user})


@router.post("", response_class=HTMLResponse)
def create(
    request: Request,
    reader_email: str = Form(...),
    book_id: int = Form(...),
    user: User = Depends(require_role(UserRole.LIBRARIAN)),
    db: Session = Depends(get_db),
):
    reader = user_repository.get_by_email(db, reader_email)
    if reader is None:
        return templates.TemplateResponse(
            request, "loans/_error.html", {"message": "Lector no encontrado."}
        )
    try:
        loan_service.create_loan(db, user=reader, book_id=book_id)
    except loan_service.LoanError as exc:
        return templates.TemplateResponse(request, "loans/_error.html", {"message": str(exc)})
    loans = loan_repository.list_all(db)
    return templates.TemplateResponse(request, "loans/_rows.html", {"loans": loans})


@router.post("/{loan_id}/return", response_class=HTMLResponse)
def give_back(
    request: Request,
    loan_id: int,
    user: User = Depends(require_role(UserRole.LIBRARIAN)),
    db: Session = Depends(get_db),
):
    try:
        loan_service.return_loan(db, loan_id=loan_id)
    except loan_service.LoanError as exc:
        return templates.TemplateResponse(request, "loans/_error.html", {"message": str(exc)})
    loans = loan_repository.list_all(db)
    return templates.TemplateResponse(request, "loans/_rows.html", {"loans": loans})


@router.post("/{loan_id}/pay-fine", response_class=HTMLResponse)
def pay_fine(
    request: Request,
    loan_id: int,
    user: User = Depends(require_role(UserRole.LIBRARIAN)),
    db: Session = Depends(get_db),
):
    try:
        loan_service.pay_fine(db, loan_id=loan_id)
    except loan_service.LoanError as exc:
        return templates.TemplateResponse(request, "loans/_error.html", {"message": str(exc)})
    loans = loan_repository.list_all(db)
    return templates.TemplateResponse(request, "loans/_rows.html", {"loans": loans})
