from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.book import Book


def create(db: Session, **fields) -> Book:
    book = Book(**fields)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_by_id(db: Session, book_id: int) -> Book | None:
    return db.get(Book, book_id)


def get_by_isbn(db: Session, isbn: str) -> Book | None:
    return db.scalar(select(Book).where(Book.isbn == isbn))


def update(db: Session, book: Book, **fields) -> Book:
    for key, value in fields.items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book


def deactivate(db: Session, book: Book) -> Book:
    book.is_active = False
    db.commit()
    db.refresh(book)
    return book


def list_all(db: Session, *, only_active: bool = True) -> list[Book]:
    stmt = select(Book)
    if only_active:
        stmt = stmt.where(Book.is_active.is_(True))
    return list(db.scalars(stmt))


def search(
    db: Session,
    *,
    title: str | None = None,
    author: str | None = None,
    isbn: str | None = None,
    category: str | None = None,
    only_active: bool = True,
) -> list[Book]:
    stmt = select(Book)
    if only_active:
        stmt = stmt.where(Book.is_active.is_(True))
    if title:
        stmt = stmt.where(Book.title.ilike(f"%{title}%"))
    if author:
        stmt = stmt.where(Book.author.ilike(f"%{author}%"))
    if isbn:
        stmt = stmt.where(Book.isbn.ilike(f"%{isbn}%"))
    if category:
        stmt = stmt.where(Book.category.ilike(f"%{category}%"))
    return list(db.scalars(stmt))


def search_any(db: Session, query: str, *, only_active: bool = True) -> list[Book]:
    stmt = select(Book)
    if only_active:
        stmt = stmt.where(Book.is_active.is_(True))
    needle = f"%{query}%"
    stmt = stmt.where(
        or_(
            Book.title.ilike(needle),
            Book.author.ilike(needle),
            Book.isbn.ilike(needle),
            Book.category.ilike(needle),
        )
    )
    return list(db.scalars(stmt))


def decrement_available(db: Session, book: Book) -> Book:
    book.available_copies -= 1
    db.commit()
    db.refresh(book)
    return book


def increment_available(db: Session, book: Book) -> Book:
    book.available_copies += 1
    db.commit()
    db.refresh(book)
    return book
