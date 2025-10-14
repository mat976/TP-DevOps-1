from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'


def test_db_check():
    r = client.get('/db-check')
    assert r.status_code == 200
    body = r.json()
    assert 'database' in body
    assert body['database'] in {'ok', 'error'}