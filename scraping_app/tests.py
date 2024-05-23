from app import app
from http import HTTPStatus
from views import blacklist
import pytest


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.app_context()
    client = app.test_client()
    yield client


def test_login(client, mocker):
    mocker.patch('views.create_access_token',
                 return_value='mocked_access_token')
    response = client.post('/api/v1/login', json={
        "username": "Brian",
        "password": "123456"
    })
    assert response.status_code == HTTPStatus.CREATED
    assert b'mocked_access_token' in response.data


def test_token_successfully_blacklisted(client, mocker):
    mocker.patch('views.create_access_token',
                 return_value='mocked_access_token')
    mocker.patch('views.jwt_required', return_value="bjaksbsnamnd")
    response = client.delete(
        "/api/v1/logout",
        headers={"Authorization": "Bearer mocked_access_token"})
    assert response.status_code == 200
    assert 'test_jti' in blacklist
