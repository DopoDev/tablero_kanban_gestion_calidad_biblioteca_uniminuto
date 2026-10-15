# RF-02 / RF-03: registrar, editar y buscar libros.
import pytest

from app.services import book_service
from tests.conftest import make_book


def test_register_book_sets_available_equal_to_total(db_session):
    book = book_service.register_book(
        db_session,
        isbn="111-1",
        title="Clean Code",
        author="Robert Martin",
        category="Software",
        total_copies=3,
    )
    assert book.available_copies == 3


def test_register_book_rejects_duplicate_isbn(db_session):
    book_service.register_book(
        db_session, isbn="111-2", title="A", author="A", category="A", total_copies=1
    )
    with pytest.raises(book_service.BookError):
        book_service.register_book(
            db_session, isbn="111-2", title="B", author="B", category="B", total_copies=1
        )


def test_register_book_rejects_zero_copies(db_session):
    with pytest.raises(book_service.BookError):
        book_service.register_book(
            db_session, isbn="111-3", title="A", author="A", category="A", total_copies=0
        )


def test_search_books_by_title(db_session):
    make_book(db_session, title="Clean Code", isbn="222-1")
    make_book(db_session, title="Otro libro", isbn="222-2")

    results = book_service.search_books(db_session, title="Clean")

    assert len(results) == 1
    assert results[0].title == "Clean Code"


def test_search_books_unit_mocks_repository(db_session, mocker):
    spy = mocker.patch("app.services.book_service.book_repository.search", return_value=[])
    book_service.search_books(db_session, author="Martin")
    spy.assert_called_once_with(db_session, author="Martin")
