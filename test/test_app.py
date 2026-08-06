from http import HTTPStatus

from fastapi.testclient import TestClient

from src.schemas import UserPublic
from src.security import create_acess_token


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Olá mundo"}


def test_create_user_deve_criar_usuario(client):
    response = client.post(
        "/users/",
        json={
            "username": "luis",
            "email": "luis@email.com",
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "username": "luis",
        "email": "luis@email.com",
        "id": 1,
    }


def test_create_user_nao_deve_criar_usuario_quando_username_ja_existe(
    client, user
):
    response = client.post(
        "/users/",
        json={
            "username": user.username,
            "email": "luis@email.com",
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": "Username already exists."}


def test_create_user_nao_deve_criar_usuario_quando_email_ja_existe(
    client, user
):
    response = client.post(
        "/users/",
        json={
            "username": "luis",
            "email": user.email,
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": "Email already exists."}


def test_get_token(client, user):
    response = client.post(
        "/token",
        data={"username": user.email, "password": user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in token
    assert "token_type" in token


def test_get_token_nao_deve_retornar_token_para_usuario_invalido(client, user):
    response = client.post(
        "/token",
        data={
            "username": "email@invalido.com",
            "password": user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}


def test_get_token_nao_deve_retornar_token_com_senha_errada(client, user):
    response = client.post(
        "/token",
        data={
            "username": user.email,
            "password": "senhaerrada",
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}


def test_get_users_deve_retornar_usuarios(client: TestClient, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get("/users/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_get_user_deve_retornar_usuario(client: TestClient, user):
    response = client.get("/users/1")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }


def test_get_user_deve_retornar_user_not_found(client):
    response = client.get("/users/2")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}


def test_update_user_deve_atualizar_usuario(client, user, token):
    response = client.put(
        f"users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "luis1",
            "email": "luis1@email.com",
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": user.id,
        "username": "luis1",
        "email": "luis1@email.com",
    }


def test_update_user_deve_retornar_user_not_found(client, token):
    response = client.put(
        "users/2",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "luis1",
            "email": "luis1@email.com",
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}


def test_update_user_deve_retornar_integrity_error(client, user, token):
    client.post(
        "/users",
        json={
            "username": "usuario1",
            "email": "usuario1@email.com",
            "password": "senha",
        },
    )

    response_update = client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "usuario1",
            "email": "usuario2@email.com",
            "password": "senha2",
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        "detail": "Username or Email already exists"
    }


def test_delete_user_deve_deletar_usuario(client, user, token):
    response = client.delete(
        f"users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}


def test_delete_user_deve_retornar_user_not_found(client, token):
    response = client.delete(
        "users/2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}


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
