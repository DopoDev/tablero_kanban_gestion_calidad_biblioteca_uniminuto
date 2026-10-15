# RF-02 / RF-03 / RNF-02 / RNF-03: CRUD y busqueda de libros, con control de acceso por rol.
from tests.conftest import TestingSessionLocal, login_as, make_librarian, make_student


def _seed_librarian(email="lib@example.com"):
    db = TestingSessionLocal()
    make_librarian(db, email=email)
    db.close()


def _seed_student(email="student@example.com"):
    db = TestingSessionLocal()
    make_student(db, email=email)
    db.close()


def test_librarian_can_register_and_search_book(client):
    _seed_librarian()
    login_as(client, "lib@example.com")

    resp = client.post(
        "/books/new",
        data={
            "isbn": "978-0132350884",
            "title": "Clean Code",
            "author": "Robert Martin",
            "category": "Software",
            "total_copies": "2",
        },
    )
    assert resp.status_code == 200
    assert "registrado" in resp.text.lower()

    search_resp = client.get("/books/search", params={"q": "Clean"})
    assert "Clean Code" in search_resp.text


def test_duplicate_isbn_returns_friendly_error_not_500(client):
    _seed_librarian()
    login_as(client, "lib@example.com")
    payload = {
        "isbn": "978-0000000001",
        "title": "Libro",
        "author": "Autor",
        "category": "Cat",
        "total_copies": "1",
    }
    client.post("/books/new", data=payload)
    resp = client.post("/books/new", data=payload)

    assert resp.status_code == 200
    assert "ya existe" in resp.text.lower()


def test_student_cannot_register_book(client):
    _seed_student()
    login_as(client, "student@example.com")

    resp = client.get("/books/new")
    assert resp.status_code == 403

    resp = client.post(
        "/books/new",
        data={
            "isbn": "978-1",
            "title": "T",
            "author": "A",
            "category": "C",
            "total_copies": "1",
        },
    )
    assert resp.status_code == 403
