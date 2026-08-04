from http import HTTPStatus

from fastapi.testclient import TestClient


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Olá mundo"}


def test_root_deve_retornar_html_com_ola_mundo(client):
    response = client.get("/ola_mundo")

    assert response.status_code == HTTPStatus.OK
    assert "<h1> Olá Mundo </h1>" in response.text


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


def test_get_users_deve_retornar_usuarios(client: TestClient):
    response = client.get("/users/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "users": [
            {
                "username": "luis",
                "email": "luis@email.com",
                "id": 1,
            }
        ]
    }


def test_get_user_deve_retornar_usuario(client: TestClient):
    response = client.get("/users/1")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "luis",
        "email": "luis@email.com",
        "id": 1,
    }


def test_get_user_deve_retornar_user_not_found(client):
    response = client.get("/users/2")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}


def test_update_user_deve_atualizar_usuario(client):
    response = client.put(
        "users/1",
        json={
            "username": "luis1",
            "email": "luis1@email.com",
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "username": "luis1",
        "email": "luis1@email.com",
    }


def test_update_user_deve_retornar_user_not_found(client):
    response = client.put(
        "users/2",
        json={
            "username": "luis1",
            "email": "luis1@email.com",
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}


def test_delete_user_deve_deletar_usuario(client):
    response = client.delete("users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "username": "luis1",
        "email": "luis1@email.com",
    }


def test_delete_user_deve_retornar_user_not_found(client):
    response = client.delete("users/2")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}
