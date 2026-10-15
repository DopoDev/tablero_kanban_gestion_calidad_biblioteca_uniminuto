from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole, UserStatus


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def list_readers(db: Session) -> list[User]:
    stmt = select(User).where(User.role.in_((UserRole.STUDENT, UserRole.COMMUNITY)))
    return list(db.scalars(stmt))


def create(
    db: Session,
    *,
    name: str,
    email: str,
    password_hash: str,
    role: UserRole,
    phone: str | None = None,
    status: UserStatus = UserStatus.ACTIVE,
) -> User:
    user = User(
        name=name, email=email, password_hash=password_hash, role=role, phone=phone, status=status
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_contact(db: Session, user: User, *, phone: str | None) -> User:
    user.phone = phone
    db.commit()
    db.refresh(user)
    return user


def set_status(db: Session, user: User, *, status: UserStatus) -> User:
    user.status = status
    db.commit()
    db.refresh(user)
    return user
