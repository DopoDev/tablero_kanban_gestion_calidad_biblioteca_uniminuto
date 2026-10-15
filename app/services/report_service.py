from datetime import date

from sqlalchemy.orm import Session

from app.repositories import book_repository, loan_repository


def overdue_loans(db: Session, today: date | None = None) -> list[dict]:
    today = today or date.today()
    loans = loan_repository.list_overdue(db, today)
    return [
        {"loan": loan, "late_days": (today - loan.due_date).days}
        for loan in loans
    ]


def inventory_report(db: Session) -> list[dict]:
    books = book_repository.list_all(db)
    return [
        {
            "book": book,
            "on_loan": book.total_copies - book.available_copies,
        }
        for book in books
    ]
