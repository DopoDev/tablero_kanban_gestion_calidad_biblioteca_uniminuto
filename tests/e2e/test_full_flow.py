# Prueba de aceptacion end-to-end, trazable a RF-02, RF-04, RF-05, RF-06 y RF-07:
# un bibliotecario registra un libro con un unico ejemplar; un lector lo toma
# prestado, lo devuelve tarde (se asigna multa, luego se paga); un segundo
# lector lo toma prestado y, mientras lo tiene, un tercer lector lo reserva;
# al devolverse, la reserva del tercer lector queda disponible.
from datetime import date, timedelta

from app.repositories import book_repository, loan_repository
from tests.conftest import TestingSessionLocal, login_as, make_librarian


def test_full_library_flow(client):
    db = TestingSessionLocal()
    make_librarian(db, email="lib@example.com")
    db.close()

    login_as(client, "lib@example.com")

    # RF-02: registrar libro con un unico ejemplar.
    client.post(
        "/books/new",
        data={
            "isbn": "978-1",
            "title": "El Principito",
            "author": "Saint-Exupery",
            "category": "Clasicos",
            "total_copies": "1",
        },
    )
    db = TestingSessionLocal()
    book_id = book_repository.get_by_isbn(db, "978-1").id
    db.close()

    # RF-04: autorregistro de tres lectores.
    for name, email, role in [
        ("Ana", "ana@example.com", "STUDENT"),
        ("Luis", "luis@example.com", "COMMUNITY"),
        ("Carla", "carla@example.com", "STUDENT"),
    ]:
        client.post(
            "/auth/register",
            data={"name": name, "email": email, "password": "password123", "role": role},
        )

    login_as(client, "lib@example.com")

    # RF-05: prestar el unico ejemplar a Ana.
    client.post("/loans", data={"reader_email": "ana@example.com", "book_id": book_id})
    db = TestingSessionLocal()
    first_loan_id = loan_repository.list_all(db)[0].id
    db.close()

    # RF-06: forzar que el prestamo este vencido y devolverlo tarde.
    db = TestingSessionLocal()
    loan = loan_repository.get_by_id(db, first_loan_id)
    loan.due_date = date.today() - timedelta(days=3)
    db.commit()
    db.close()

    return_resp = client.post(f"/loans/{first_loan_id}/return")
    assert "pendiente" in return_resp.text.lower()

    pay_resp = client.post(f"/loans/{first_loan_id}/pay-fine")
    assert "pendiente" not in pay_resp.text.lower()

    # El libro vuelve a estar disponible: se presta a Luis.
    client.post("/loans", data={"reader_email": "luis@example.com", "book_id": book_id})
    db = TestingSessionLocal()
    second_loan_id = next(
        l.id for l in loan_repository.list_all(db) if l.return_date is None
    )
    db.close()

    # RF-07: mientras Luis lo tiene prestado, Carla reserva el libro agotado.
    login_as(client, "carla@example.com")
    reserve_resp = client.post("/reservations", data={"book_id": book_id})
    assert "PENDING" in reserve_resp.text

    # Al devolverse, la reserva de Carla queda disponible.
    login_as(client, "lib@example.com")
    client.post(f"/loans/{second_loan_id}/return")

    login_as(client, "carla@example.com")
    mine_resp = client.get("/reservations/mine")
    assert "AVAILABLE" in mine_resp.text
