from sqlalchemy.orm import Session

from app.models.user import User, UserStatus
from app.repositories import user_repository


class UserError(Exception):
    pass


def list_readers(db: Session) -> list[User]:
    return user_repository.list_readers(db)


def update_contact(db: Session, *, user_id: int, phone: str | None) -> User:
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise UserError("Usuario no encontrado.")
    return user_repository.update_contact(db, user, phone=phone)


def suspend_reader(db: Session, *, user_id: int) -> User:
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise UserError("Usuario no encontrado.")
    return user_repository.set_status(db, user, status=UserStatus.SUSPENDED)


def activate_reader(db: Session, *, user_id: int) -> User:
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise UserError("Usuario no encontrado.")
    return user_repository.set_status(db, user, status=UserStatus.ACTIVE)
