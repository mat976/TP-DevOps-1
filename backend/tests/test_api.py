import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_articles_returns_200():
    response = client.get("/articles")
    assert response.status_code == 200