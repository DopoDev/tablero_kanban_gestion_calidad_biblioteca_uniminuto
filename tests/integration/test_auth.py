# RF-01: autenticacion de usuarios segun su rol.


def test_register_login_and_reject_wrong_password(client):
    register_resp = client.post(
        "/auth/register",
        data={
            "name": "Ana",
            "email": "ana@example.com",
            "password": "password123",
            "role": "STUDENT",
        },
    )
    assert register_resp.status_code == 200
    assert register_resp.headers["HX-Redirect"] == "/"
    assert "session" in register_resp.cookies

    login_ok = client.post(
        "/auth/login", data={"email": "ana@example.com", "password": "password123"}
    )
    assert login_ok.status_code == 200
    assert login_ok.headers["HX-Redirect"] == "/"

    login_bad = client.post(
        "/auth/login", data={"email": "ana@example.com", "password": "wrong"}
    )
    assert login_bad.status_code == 200
    assert "HX-Redirect" not in login_bad.headers
    assert "incorrecta" in login_bad.text


def test_register_rejects_librarian_role(client):
    resp = client.post(
        "/auth/register",
        data={
            "name": "Bibliotecario",
            "email": "biblio@example.com",
            "password": "password123",
            "role": "LIBRARIAN",
        },
    )
    assert resp.status_code == 200
    assert "HX-Redirect" not in resp.headers
    assert "no permitido" in resp.text.lower()


def test_protected_route_requires_session(client):
    from fastapi import Depends

    from app.dependencies.auth import get_current_user
    from main import app

    @app.get("/_protected")
    def protected(user=Depends(get_current_user)):
        return {"email": user.email}

    resp = client.get("/_protected")
    assert resp.status_code == 401
