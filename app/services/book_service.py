from sqlalchemy.orm import Session

from app.models.book import Book
from app.repositories import book_repository


class BookError(Exception):
    pass


def register_book(
    db: Session,
    *,
    isbn: str,
    title: str,
    author: str,
    category: str,
    total_copies: int,
    description: str | None = None,
    publisher: str | None = None,
    publication_year: int | None = None,
) -> Book:
    if book_repository.get_by_isbn(db, isbn):
        raise BookError("Ya existe un libro con ese ISBN.")
    if total_copies < 1:
        raise BookError("El numero de ejemplares debe ser al menos 1.")
    return book_repository.create(
        db,
        isbn=isbn,
        title=title,
        author=author,
        category=category,
        description=description,
        publisher=publisher,
        publication_year=publication_year,
        total_copies=total_copies,
        available_copies=total_copies,
    )


def update_book(db: Session, *, book_id: int, **fields) -> Book:
    book = book_repository.get_by_id(db, book_id)
    if book is None:
        raise BookError("Libro no encontrado.")
    new_isbn = fields.get("isbn")
    if new_isbn and new_isbn != book.isbn and book_repository.get_by_isbn(db, new_isbn):
        raise BookError("Ya existe un libro con ese ISBN.")
    return book_repository.update(db, book, **fields)


def deactivate_book(db: Session, *, book_id: int) -> Book:
    book = book_repository.get_by_id(db, book_id)
    if book is None:
        raise BookError("Libro no encontrado.")
    return book_repository.deactivate(db, book)


def search_books(db: Session, *, query: str | None = None, **filters) -> list[Book]:
    if query:
        return book_repository.search_any(db, query)
    return book_repository.search(db, **filters)


def list_books(db: Session) -> list[Book]:
    return book_repository.list_all(db)
