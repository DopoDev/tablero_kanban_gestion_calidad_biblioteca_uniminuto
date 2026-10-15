# RF-07: reservar titulos sin ejemplares disponibles y notificar cuando se liberen.
from datetime import date

import pytest

from app.services import loan_service, reservation_service
from tests.conftest import make_book, make_student

TODAY = date(2026, 1, 1)


def test_create_reservation_rejected_when_copies_available(db_session):
    student = make_student(db_session)
    book = make_book(db_session, available_copies=1)
    with pytest.raises(reservation_service.ReservationError):
        reservation_service.create_reservation(db_session, user=student, book_id=book.id)


def test_create_reservation_allowed_when_no_copies_available(db_session):
    student = make_student(db_session)
    book = make_book(db_session, available_copies=0)
    reservation = reservation_service.create_reservation(db_session, user=student, book_id=book.id)
    assert reservation.id is not None


def test_notify_if_available_does_nothing_without_free_copy(db_session):
    student = make_student(db_session)
    book = make_book(db_session, available_copies=0)
    reservation_service.create_reservation(db_session, user=student, book_id=book.id)

    reservation_service.notify_if_available(db_session, book.id)

    reservations = reservation_service.list_my_reservations(db_session, student)
    assert reservations[0].status.value == "PENDING"


def test_notify_if_available_flips_oldest_pending_reservation(db_session):
    student = make_student(db_session)
    other_borrower = make_student(db_session)
    book = make_book(db_session, total_copies=1, available_copies=1)

    loan = loan_service.create_loan(db_session, user=other_borrower, book_id=book.id, today=TODAY)
    reservation = reservation_service.create_reservation(db_session, user=student, book_id=book.id)

    loan_service.return_loan(db_session, loan_id=loan.id, today=TODAY)

    reservations = reservation_service.list_my_reservations(db_session, student)
    assert reservations[0].id == reservation.id
    assert reservations[0].status.value == "AVAILABLE"
