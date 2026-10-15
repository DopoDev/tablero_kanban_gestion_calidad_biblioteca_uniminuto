from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.services import auth_service


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    cookie = request.cookies.get(auth_service.SESSION_COOKIE)
    data = auth_service.read_session_cookie(cookie) if cookie else None
    if data is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No has iniciado sesion.")
    user = db.get(User, data["user_id"])
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No has iniciado sesion.")
    return user


def require_role(*roles: UserRole):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permiso para esto.")
        return user

    return dependency
