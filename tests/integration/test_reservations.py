# RF-07: reservar libros agotados y notificacion de disponibilidad al devolver.
from tests.conftest import (
    TestingSessionLocal,
    login_as,
    make_book,
    make_librarian,
    make_student,
)


def test_reserve_and_get_notified_when_available(client):
    db = TestingSessionLocal()
    make_librarian(db, email="lib@example.com")
    make_student(db, email="borrower@example.com")
    make_student(db, email="reserver@example.com")
    book = make_book(db, isbn="RES-1", total_copies=1, available_copies=1)
    book_id = book.id
    db.close()

    login_as(client, "lib@example.com")
    client.post("/loans", data={"reader_email": "borrower@example.com", "book_id": book_id})

    login_as(client, "reserver@example.com")
    reserve_resp = client.post("/reservations", data={"book_id": book_id})
    assert reserve_resp.status_code == 200
    assert "PENDING" in reserve_resp.text

    db = TestingSessionLocal()
    from app.repositories import loan_repository

    loan = loan_repository.list_all(db)[0]
    loan_id = loan.id
    db.close()

    login_as(client, "lib@example.com")
    client.post(f"/loans/{loan_id}/return")

    login_as(client, "reserver@example.com")
    mine_resp = client.get("/reservations/mine")
    assert "AVAILABLE" in mine_resp.text
