from http import HTTPStatus


def test_get_token(client, user):
    response = client.post(
        "auth/token",
        data={"username": user.email, "password": user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in token
    assert "token_type" in token


def test_get_token_nao_deve_retornar_token_para_usuario_invalido(client, user):
    response = client.post(
        "/auth/token",
        data={
            "username": "email@invalido.com",
            "password": user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}


def test_get_token_nao_deve_retornar_token_com_senha_errada(client, user):
    response = client.post(
        "/auth/token",
        data={
            "username": user.email,
            "password": "senhaerrada",
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}
