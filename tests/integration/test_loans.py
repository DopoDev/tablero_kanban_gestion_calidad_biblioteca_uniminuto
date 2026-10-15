# RF-05 / RF-06 / RNF-02: flujo HTTP de prestamos, devoluciones y multas por rol.
from app.models.user import UserStatus
from tests.conftest import (
    TestingSessionLocal,
    login_as,
    make_book,
    make_librarian,
    make_student,
)


def test_only_librarian_can_create_loans(client):
    db = TestingSessionLocal()
    make_librarian(db, email="lib@example.com")
    make_student(db, email="student@example.com")
    book = make_book(db, isbn="LOAN-1")
    db.close()

    login_as(client, "student@example.com")
    resp = client.post("/loans", data={"reader_email": "student@example.com", "book_id": book.id})
    assert resp.status_code == 403


def test_create_return_and_fine_flow(client):
    db = TestingSessionLocal()
    make_librarian(db, email="lib@example.com")
    make_student(db, email="student@example.com")
    book = make_book(db, isbn="LOAN-2", total_copies=1, available_copies=1)
    book_id = book.id
    db.close()

    login_as(client, "lib@example.com")

    create_resp = client.post(
        "/loans", data={"reader_email": "student@example.com", "book_id": book_id}
    )
    assert create_resp.status_code == 200
    assert "student@example.com" not in create_resp.text  # tabla usa user_id, no email

    db = TestingSessionLocal()
    from app.repositories import loan_repository

    loan = loan_repository.list_all(db)[0]
    loan_id = loan.id
    db.close()

    return_resp = client.post(f"/loans/{loan_id}/return")
    assert return_resp.status_code == 200
    assert "0" in return_resp.text  # sin retraso, multa 0


def test_suspended_reader_is_blocked_from_borrowing(client):
    db = TestingSessionLocal()
    make_librarian(db, email="lib@example.com")
    make_student(db, email="student@example.com", status=UserStatus.SUSPENDED)
    book = make_book(db, isbn="LOAN-3")
    book_id = book.id
    db.close()

    login_as(client, "lib@example.com")
    resp = client.post(
        "/loans", data={"reader_email": "student@example.com", "book_id": book_id}
    )
    assert "suspendido" in resp.text.lower()
