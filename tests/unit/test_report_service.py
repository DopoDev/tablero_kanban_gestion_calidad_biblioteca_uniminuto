# RF-08: reportes de prestamos vencidos e inventario.
from datetime import date, timedelta

from app.services import loan_service, report_service
from tests.conftest import make_book, make_student

TODAY = date(2026, 1, 1)


def test_overdue_loans_excludes_due_today_includes_due_yesterday(db_session):
    student = make_student(db_session)
    due_today_book = make_book(db_session)
    overdue_book = make_book(db_session)

    loan_due_today = loan_service.create_loan(
        db_session, user=student, book_id=due_today_book.id, today=TODAY - timedelta(days=loan_service.LOAN_DURATION_DAYS)
    )
    loan_overdue = loan_service.create_loan(
        db_session,
        user=student,
        book_id=overdue_book.id,
        today=TODAY - timedelta(days=loan_service.LOAN_DURATION_DAYS + 1),
    )

    rows = report_service.overdue_loans(db_session, today=TODAY)

    overdue_ids = {row["loan"].id for row in rows}
    assert loan_due_today.id not in overdue_ids
    assert loan_overdue.id in overdue_ids


def test_inventory_report_counts_on_loan_copies(db_session):
    student = make_student(db_session)
    book = make_book(db_session, total_copies=3, available_copies=3)
    loan_service.create_loan(db_session, user=student, book_id=book.id, today=TODAY)

    rows = report_service.inventory_report(db_session)

    row = next(r for r in rows if r["book"].id == book.id)
    assert row["on_loan"] == 1
