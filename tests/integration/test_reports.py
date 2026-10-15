# RF-08 / RNF-02: reportes de inventario y prestamos vencidos, solo para bibliotecario.
from tests.conftest import (
    TestingSessionLocal,
    login_as,
    make_book,
    make_librarian,
    make_student,
)


def test_only_librarian_can_see_reports(client):
    db = TestingSessionLocal()
    make_librarian(db, email="lib@example.com")
    make_student(db, email="student@example.com")
    db.close()

    login_as(client, "student@example.com")
    assert client.get("/reports/overdue").status_code == 403
    assert client.get("/reports/inventory").status_code == 403

    login_as(client, "lib@example.com")
    assert client.get("/reports/overdue").status_code == 200
    assert client.get("/reports/inventory").status_code == 200


def test_inventory_report_shows_registered_books(client):
    db = TestingSessionLocal()
    make_librarian(db, email="lib@example.com")
    make_book(db, isbn="REP-1", title="Libro Reportado")
    db.close()

    login_as(client, "lib@example.com")
    resp = client.get("/reports/inventory")
    assert "Libro Reportado" in resp.text
