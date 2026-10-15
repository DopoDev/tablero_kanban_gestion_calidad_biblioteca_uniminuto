from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.loan import Loan


def create(db: Session, **fields) -> Loan:
    loan = Loan(**fields)
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def get_by_id(db: Session, loan_id: int) -> Loan | None:
    return db.get(Loan, loan_id)


def count_active_for_user(db: Session, user_id: int) -> int:
    stmt = select(func.count()).select_from(Loan).where(
        Loan.user_id == user_id, Loan.return_date.is_(None)
    )
    return db.scalar(stmt) or 0


def has_unpaid_fine(db: Session, user_id: int) -> bool:
    stmt = select(Loan).where(Loan.user_id == user_id, Loan.fine_paid.is_(False))
    return db.scalar(stmt) is not None


def list_active_for_user(db: Session, user_id: int) -> list[Loan]:
    stmt = select(Loan).where(Loan.user_id == user_id, Loan.return_date.is_(None))
    return list(db.scalars(stmt))


def list_all(db: Session) -> list[Loan]:
    return list(db.scalars(select(Loan)))


def list_overdue(db: Session, today: date) -> list[Loan]:
    stmt = select(Loan).where(Loan.return_date.is_(None), Loan.due_date < today)
    return list(db.scalars(stmt))


def mark_returned(db: Session, loan: Loan, *, return_date: date, fine_amount: float) -> Loan:
    loan.return_date = return_date
    loan.fine_amount = fine_amount
    loan.fine_paid = fine_amount == 0
    db.commit()
    db.refresh(loan)
    return loan


def pay_fine(db: Session, loan: Loan) -> Loan:
    loan.fine_paid = True
    db.commit()
    db.refresh(loan)
    return loan
