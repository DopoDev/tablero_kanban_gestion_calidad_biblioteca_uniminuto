from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models.book import Book
from app.models.user import User, UserRole
from app.services import book_service
from app.templates import templates

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_class=HTMLResponse)
def index(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    books = book_service.list_books(db)
    return templates.TemplateResponse(request, "books/index.html", {"user": user, "books": books})


@router.get("/search", response_class=HTMLResponse)
def search(
    request: Request,
    q: str = "",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    books = book_service.search_books(db, query=q) if q else book_service.list_books(db)
    return templates.TemplateResponse(request, "books/_results.html", {"books": books})


@router.get("/new", response_class=HTMLResponse)
def new_form(request: Request, user: User = Depends(require_role(UserRole.LIBRARIAN))):
    return templates.TemplateResponse(request, "books/form.html", {"book": None, "user": user})


@router.post("/new", response_class=HTMLResponse)
def create(
    request: Request,
    isbn: str = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    category: str = Form(...),
    total_copies: int = Form(...),
    description: str = Form(""),
    publisher: str = Form(""),
    publication_year: int | None = Form(None),
    user: User = Depends(require_role(UserRole.LIBRARIAN)),
    db: Session = Depends(get_db),
):
    try:
        book_service.register_book(
            db,
            isbn=isbn,
            title=title,
            author=author,
            category=category,
            total_copies=total_copies,
            description=description or None,
            publisher=publisher or None,
            publication_year=publication_year,
        )
    except book_service.BookError as exc:
        return templates.TemplateResponse(
            request, "books/_error.html", {"message": str(exc)}
        )
    return templates.TemplateResponse(
        request, "books/_error.html", {"message": "Libro registrado.", "ok": True}
    )


def _get_book_or_404(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if book is None:
        raise book_service.BookError("Libro no encontrado.")
    return book


@router.get("/{book_id}/edit", response_class=HTMLResponse)
def edit_form(
    request: Request,
    book_id: int,
    user: User = Depends(require_role(UserRole.LIBRARIAN)),
    db: Session = Depends(get_db),
):
    book = _get_book_or_404(db, book_id)
    return templates.TemplateResponse(request, "books/form.html", {"book": book, "user": user})


@router.post("/{book_id}/edit", response_class=HTMLResponse)
def edit_submit(
    request: Request,
    book_id: int,
    isbn: str = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    category: str = Form(...),
    total_copies: int = Form(...),
    description: str = Form(""),
    publisher: str = Form(""),
    publication_year: int | None = Form(None),
    user: User = Depends(require_role(UserRole.LIBRARIAN)),
    db: Session = Depends(get_db),
):
    try:
        book_service.update_book(
            db,
            book_id=book_id,
            isbn=isbn,
            title=title,
            author=author,
            category=category,
            total_copies=total_copies,
            description=description or None,
            publisher=publisher or None,
            publication_year=publication_year,
        )
    except book_service.BookError as exc:
        return templates.TemplateResponse(
            request, "books/_error.html", {"message": str(exc)}
        )
    return templates.TemplateResponse(
        request, "books/_error.html", {"message": "Libro actualizado.", "ok": True}
    )


@router.post("/{book_id}/deactivate", response_class=HTMLResponse)
def deactivate(
    request: Request,
    book_id: int,
    user: User = Depends(require_role(UserRole.LIBRARIAN)),
    db: Session = Depends(get_db),
):
    try:
        book_service.deactivate_book(db, book_id=book_id)
    except book_service.BookError as exc:
        return templates.TemplateResponse(
            request, "books/_error.html", {"message": str(exc)}
        )
    return templates.TemplateResponse(
        request, "books/_error.html", {"message": "Libro dado de baja.", "ok": True}
    )
