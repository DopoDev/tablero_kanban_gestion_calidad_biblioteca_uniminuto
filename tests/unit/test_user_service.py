# RF-04: registrar lectores con datos de contacto y estado (activo/suspendido).
import pytest

from app.models.user import UserStatus
from app.services import user_service
from tests.conftest import make_student


def test_suspend_then_activate_reader(db_session):
    student = make_student(db_session)

    suspended = user_service.suspend_reader(db_session, user_id=student.id)
    assert suspended.status == UserStatus.SUSPENDED

    activated = user_service.activate_reader(db_session, user_id=student.id)
    assert activated.status == UserStatus.ACTIVE


def test_update_contact_sets_phone(db_session):
    student = make_student(db_session)
    updated = user_service.update_contact(db_session, user_id=student.id, phone="3001234567")
    assert updated.phone == "3001234567"


def test_suspend_unknown_user_raises(db_session):
    with pytest.raises(user_service.UserError):
        user_service.suspend_reader(db_session, user_id=999999)
