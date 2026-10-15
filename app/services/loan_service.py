from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.loan import Loan
from app.models.user import User, UserStatus
from app.repositories import book_repository, loan_repository
from app.services import reservation_service

LOAN_DURATION_DAYS = 7
FINE_PER_DAY = 500
MAX_ACTIVE_LOANS = 3


class LoanError(Exception):
    pass


def create_loan(db: Session, *, user: User, book_id: int, today: date | None = None) -> Loan:
    today = today or date.today()
    book = book_repository.get_by_id(db, book_id)
    if book is None or not book.is_active:
        raise LoanError("Libro no encontrado.")
    if user.status == UserStatus.SUSPENDED:
        raise LoanError("El usuario esta suspendido.")
    if loan_repository.has_unpaid_fine(db, user.id):
        raise LoanError("El usuario tiene multas pendientes.")
    if loan_repository.count_active_for_user(db, user.id) >= MAX_ACTIVE_LOANS:
        raise LoanError("El usuario alcanzo el limite de prestamos activos.")
    if book.available_copies <= 0:
        raise LoanError("No hay ejemplares disponibles.")

    book_repository.decrement_available(db, book)
    return loan_repository.create(
        db,
        user_id=user.id,
        book_id=book.id,
        loan_date=today,
        due_date=today + timedelta(days=LOAN_DURATION_DAYS),
    )


def return_loan(db: Session, *, loan_id: int, today: date | None = None) -> Loan:
    today = today or date.today()
    loan = loan_repository.get_by_id(db, loan_id)
    if loan is None or loan.return_date is not None:
        raise LoanError("Prestamo invalido o ya devuelto.")

    late_days = max(0, (today - loan.due_date).days)
    fine = late_days * FINE_PER_DAY
    loan = loan_repository.mark_returned(db, loan, return_date=today, fine_amount=fine)

    book = book_repository.get_by_id(db, loan.book_id)
    book_repository.increment_available(db, book)
    reservation_service.notify_if_available(db, loan.book_id)
    return loan


def pay_fine(db: Session, *, loan_id: int) -> Loan:
    loan = loan_repository.get_by_id(db, loan_id)
    if loan is None:
        raise LoanError("Prestamo no encontrado.")
    return loan_repository.pay_fine(db, loan)
