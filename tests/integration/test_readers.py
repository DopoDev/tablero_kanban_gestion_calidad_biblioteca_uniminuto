# RF-04 / RNF-02: gestion de estado de lectores restringida al bibliotecario.
from tests.conftest import TestingSessionLocal, login_as, make_librarian, make_student


def test_only_librarian_can_list_and_suspend_readers(client):
    db = TestingSessionLocal()
    make_librarian(db, email="lib@example.com")
    reader = make_student(db, email="reader@example.com")
    reader_id = reader.id
    db.close()

    login_as(client, "reader@example.com")
    assert client.get("/readers").status_code == 403
    assert client.post(f"/readers/{reader_id}/suspend").status_code == 403

    login_as(client, "lib@example.com")
    resp = client.get("/readers")
    assert resp.status_code == 200
    assert "reader@example.com" in resp.text

    suspend_resp = client.post(f"/readers/{reader_id}/suspend")
    assert "SUSPENDED" in suspend_resp.text

    activate_resp = client.post(f"/readers/{reader_id}/activate")
    assert "ACTIVE" in activate_resp.text
