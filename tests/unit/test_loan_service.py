# RF-05 / RF-06: registrar prestamos y calcular multas por retraso.
from datetime import date, timedelta

import pytest

from app.models.user import UserStatus
from app.repositories import loan_repository
from app.services import loan_service
from tests.conftest import make_book, make_student

TODAY = date(2026, 1, 1)


# Tabla de decision RF-05: disponible x multas_pendientes x limite_alcanzado
@pytest.mark.parametrize(
    "available, has_fine, at_limit, should_succeed",
    [
        (True, False, False, True),  # unico caso que debe prestar
        (False, False, False, False),  # sin ejemplares
        (True, True, False, False),  # multa pendiente
        (True, False, True, False),  # limite alcanzado
        (False, True, False, False),
        (False, False, True, False),
        (True, True, True, False),
        (False, True, True, False),
    ],
)
def test_create_loan_decision_table(db_session, available, has_fine, at_limit, should_succeed):
    student = make_student(db_session)
    book = make_book(db_session, available_copies=1 if available else 0)

    if at_limit:
        for _ in range(loan_service.MAX_ACTIVE_LOANS):
            filler = make_book(db_session)
            loan_service.create_loan(db_session, user=student, book_id=filler.id, today=TODAY)

    if has_fine:
        # Se crea directo por repositorio (no por el servicio) para no chocar
        # con el propio limite de prestamos activos que se arma arriba.
        other_book = make_book(db_session)
        old_loan = loan_repository.create(
            db_session,
            user_id=student.id,
            book_id=other_book.id,
            loan_date=TODAY,
            due_date=TODAY,
        )
        loan_repository.mark_returned(
            db_session, old_loan, return_date=TODAY, fine_amount=500
        )

    if should_succeed:
        loan = loan_service.create_loan(db_session, user=student, book_id=book.id, today=TODAY)
        assert loan.due_date == TODAY + timedelta(days=loan_service.LOAN_DURATION_DAYS)
    else:
        with pytest.raises(loan_service.LoanError):
            loan_service.create_loan(db_session, user=student, book_id=book.id, today=TODAY)


def test_create_loan_rejects_suspended_user(db_session):
    student = make_student(db_session, status=UserStatus.SUSPENDED)
    book = make_book(db_session)
    with pytest.raises(loan_service.LoanError):
        loan_service.create_loan(db_session, user=student, book_id=book.id, today=TODAY)


# Valores limite: 2 prestamos activos -> el 3ro procede, el 4to falla.
def test_third_loan_succeeds_fourth_fails(db_session):
    student = make_student(db_session)
    for _ in range(2):
        loan_service.create_loan(db_session, user=student, book_id=make_book(db_session).id, today=TODAY)

    third = loan_service.create_loan(db_session, user=student, book_id=make_book(db_session).id, today=TODAY)
    assert third is not None

    with pytest.raises(loan_service.LoanError):
        loan_service.create_loan(db_session, user=student, book_id=make_book(db_session).id, today=TODAY)


@pytest.mark.parametrize(
    "days_after_due, expected_fine",
    [
        (-1, 0),  # devuelto antes de vencer
        (0, 0),  # devuelto justo el dia de vencimiento
        (1, loan_service.FINE_PER_DAY),
        (5, 5 * loan_service.FINE_PER_DAY),
    ],
)
def test_return_loan_fine_boundaries(db_session, days_after_due, expected_fine):
    student = make_student(db_session)
    book = make_book(db_session)
    loan = loan_service.create_loan(db_session, user=student, book_id=book.id, today=TODAY)

    return_date = loan.due_date + timedelta(days=days_after_due)
    returned = loan_service.return_loan(db_session, loan_id=loan.id, today=return_date)

    assert float(returned.fine_amount) == expected_fine
    assert returned.fine_paid == (expected_fine == 0)


def test_return_loan_restores_available_copies(db_session):
    student = make_student(db_session)
    book = make_book(db_session, total_copies=1, available_copies=1)
    loan = loan_service.create_loan(db_session, user=student, book_id=book.id, today=TODAY)
    assert book.available_copies == 0

    loan_service.return_loan(db_session, loan_id=loan.id, today=TODAY)
    db_session.refresh(book)
    assert book.available_copies == 1


def test_create_loan_uses_mocked_repositories(db_session, mocker):
    student = make_student(db_session)
    book = make_book(db_session)
    mocker.patch(
        "app.services.loan_service.loan_repository.count_active_for_user", return_value=0
    )
    spy = mocker.patch(
        "app.services.loan_service.loan_repository.create", wraps=loan_repository.create
    )

    loan_service.create_loan(db_session, user=student, book_id=book.id, today=TODAY)

    spy.assert_called_once()
