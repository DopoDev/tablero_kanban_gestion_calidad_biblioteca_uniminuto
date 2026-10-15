from datetime import date

from sqlalchemy.orm import Session

from app.models.reservation import Reservation
from app.models.user import User
from app.repositories import book_repository, reservation_repository


class ReservationError(Exception):
    pass


def create_reservation(
    db: Session, *, user: User, book_id: int, today: date | None = None
) -> Reservation:
    book = book_repository.get_by_id(db, book_id)
    if book is None or not book.is_active:
        raise ReservationError("Libro no encontrado.")
    if book.available_copies > 0:
        raise ReservationError(
            "El libro tiene ejemplares disponibles, solicita el prestamo directamente."
        )
    return reservation_repository.create(
        db, user_id=user.id, book_id=book.id, reservation_date=today or date.today()
    )


def notify_if_available(db: Session, book_id: int) -> None:
    book = book_repository.get_by_id(db, book_id)
    if book is None or book.available_copies <= 0:
        return
    reservation = reservation_repository.oldest_pending_for_book(db, book_id)
    if reservation:
        reservation_repository.mark_available(db, reservation)


def list_my_reservations(db: Session, user: User) -> list[Reservation]:
    return reservation_repository.list_for_user(db, user.id)
