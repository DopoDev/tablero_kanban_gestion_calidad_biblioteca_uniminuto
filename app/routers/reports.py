from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_role
from app.models.user import User, UserRole
from app.services import report_service
from app.templates import templates

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/overdue", response_class=HTMLResponse)
def overdue(
    request: Request,
    user: User = Depends(require_role(UserRole.LIBRARIAN)),
    db: Session = Depends(get_db),
):
    rows = report_service.overdue_loans(db)
    return templates.TemplateResponse(request, "reports/overdue.html", {"rows": rows, "user": user})


@router.get("/inventory", response_class=HTMLResponse)
def inventory(
    request: Request,
    user: User = Depends(require_role(UserRole.LIBRARIAN)),
    db: Session = Depends(get_db),
):
    rows = report_service.inventory_report(db)
    return templates.TemplateResponse(
        request, "reports/inventory.html", {"rows": rows, "user": user}
    )
