from http import HTTPStatus

from fastapi.testclient import TestClient

from src.app import app


def test_root_deve_retornar_ok_e_ola_mundo():
    client = TestClient(app)  # Arrange

    response = client.get("/")  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {"message": "Olá mundo"}


def test_root_deve_retornar_html_com_ola_mundo():
    client = TestClient(app)

    response = client.get("/ola_mundo")

    assert response.status_code == HTTPStatus.OK
    assert "<h1> Olá Mundo </h1>" in response.text
