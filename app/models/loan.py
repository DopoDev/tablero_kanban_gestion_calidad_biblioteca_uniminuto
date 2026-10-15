from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False, index=True)
    loan_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    return_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    fine_amount: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False, default=0)
    fine_paid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
