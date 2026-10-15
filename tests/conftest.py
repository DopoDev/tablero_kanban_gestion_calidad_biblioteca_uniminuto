import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models.user import User, UserRole
from app.repositories import book_repository, user_repository
from app.services import auth_service
from main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


_counter = {"n": 0}


def _unique(prefix: str) -> str:
    _counter["n"] += 1
    return f"{prefix}{_counter['n']}"


def make_user(db, *, role: UserRole, **overrides) -> User:
    defaults = {
        "name": _unique("Usuario"),
        "email": f"{_unique('user')}@example.com",
        "password": "password123",
    }
    defaults.update(overrides)
    password_hash = auth_service.password_hasher.hash(defaults.pop("password"))
    return user_repository.create(db, role=role, password_hash=password_hash, **defaults)


def make_librarian(db, **overrides) -> User:
    return make_user(db, role=UserRole.LIBRARIAN, **overrides)


def make_student(db, **overrides) -> User:
    return make_user(db, role=UserRole.STUDENT, **overrides)


def make_community(db, **overrides) -> User:
    return make_user(db, role=UserRole.COMMUNITY, **overrides)


def make_book(db, **overrides):
    defaults = {
        "isbn": _unique("ISBN-"),
        "title": "Libro de prueba",
        "author": "Autor de prueba",
        "category": "General",
        "total_copies": 1,
        "available_copies": 1,
        "description": None,
        "publisher": None,
        "publication_year": None,
        "is_active": True,
    }
    defaults.update(overrides)
    return book_repository.create(db, **defaults)


def login_as(client: TestClient, email: str, password: str = "password123") -> TestClient:
    client.post("/auth/login", data={"email": email, "password": password})
    return client
