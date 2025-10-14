import pytest
from app import app, validate_login_input

def test_validate_login_input():
    # Usuário e senha válidos
    assert validate_login_input('usuario', 'senha123') is True
    # Usuário vazio
    assert validate_login_input('', 'senha123') is False
    # Senha curta
    assert validate_login_input('usuario', '123') is False
    # Caracteres perigosos
    assert validate_login_input("admin'--", 'senha123') is False
    assert validate_login_input('admin;', 'senha123') is False

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_login_success(client):
    response = client.post('/login', data={'username': 'admin', 'password': 'senha123'})
    assert b'Login bem-sucedido' in response.data
    assert response.status_code == 200

def test_login_fail(client):
    response = client.post('/login', data={'username': 'admin', 'password': 'errada'})
    assert 'Credenciais inválidas' in response.data.decode('utf-8')
    assert response.status_code == 401

def test_login_invalid_input(client):
    response = client.post('/login', data={'username': '', 'password': 'senha123'})
    assert 'Credenciais inválidas' in response.data.decode('utf-8')
    assert response.status_code == 400
    response = client.post('/login', data={'username': 'admin;', 'password': 'senha123'})
    assert 'Credenciais inválidas' in response.data.decode('utf-8')
    assert response.status_code == 400

def test_user_info_requires_token(client):
    response = client.get('/user_info?id=admin')
    assert b'Token ausente' in response.data
    assert response.status_code == 401

def test_admin_panel_requires_token(client):
    response = client.get('/secret-admin-panel')
    assert b'Token ausente' in response.data
    assert response.status_code == 401
