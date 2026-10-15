from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.reservation import Reservation, ReservationStatus


def create(db: Session, **fields) -> Reservation:
    reservation = Reservation(**fields)
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def oldest_pending_for_book(db: Session, book_id: int) -> Reservation | None:
    stmt = (
        select(Reservation)
        .where(Reservation.book_id == book_id, Reservation.status == ReservationStatus.PENDING)
        .order_by(Reservation.reservation_date, Reservation.id)
    )
    return db.scalar(stmt)


def list_for_user(db: Session, user_id: int) -> list[Reservation]:
    stmt = select(Reservation).where(Reservation.user_id == user_id)
    return list(db.scalars(stmt))


def mark_available(db: Session, reservation: Reservation) -> Reservation:
    reservation.status = ReservationStatus.AVAILABLE
    db.commit()
    db.refresh(reservation)
    return reservation


def cancel(db: Session, reservation: Reservation) -> Reservation:
    reservation.status = ReservationStatus.CANCELLED
    db.commit()
    db.refresh(reservation)
    return reservation
