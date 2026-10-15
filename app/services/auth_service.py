from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User, UserRole
from app.repositories import user_repository

password_hasher = PasswordHash.recommended()
_serializer = URLSafeTimedSerializer(settings.secret_key, salt="session")

SESSION_COOKIE = "session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 dias


class AuthError(Exception):
    pass


def register(
    db: Session,
    *,
    name: str,
    email: str,
    password: str,
    role: UserRole,
    phone: str | None = None,
) -> User:
    if user_repository.get_by_email(db, email):
        raise AuthError("Ya existe una cuenta con ese correo.")
    password_hash = password_hasher.hash(password)
    return user_repository.create(
        db, name=name, email=email, password_hash=password_hash, role=role, phone=phone
    )


def authenticate(db: Session, *, email: str, password: str) -> User:
    user = user_repository.get_by_email(db, email)
    if user is None:
        raise AuthError("No se encontró el correo electrónico.")
    if not password_hasher.verify(password, user.password_hash):
        raise AuthError("contrasena incorrecta.")
    return user


def create_session_cookie(user: User) -> str:
    return _serializer.dumps({"user_id": user.id, "role": user.role.value})


def read_session_cookie(value: str) -> dict | None:
    try:
        return _serializer.loads(value, max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
