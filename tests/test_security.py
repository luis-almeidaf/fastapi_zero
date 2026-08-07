from http import HTTPStatus

from jwt import decode

from src.security import create_acess_token, settings


def test_jwt():
    data = {"test": "test"}
    token = create_acess_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=["HS256"])

    assert decoded["test"] == data["test"]
    assert "exp" in decoded


def test_jwt_invalid_token(client):
    response = client.delete(
        "/users/1", headers={"Authorization": "Bearer token-invalido"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_jwt_email_invalido(client):
    token = create_acess_token(data={"sub": "email-invalido"})
    response = client.delete(
        "/users/1", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_jwt_usuario_nao_cadastrasdo(client):
    token = create_acess_token(data={"sub": ""})
    response = client.delete(
        "/users/1", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
