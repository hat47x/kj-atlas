from fastapi.testclient import TestClient

from kj_atlas_api.main import app
from kj_atlas_api.settings import settings


def test_allows_requests_when_api_key_is_unset() -> None:
    original = settings.api_key
    settings.api_key = None
    try:
        with TestClient(app) as client:
            response = client.get('/not-found')
            assert response.status_code == 404
    finally:
        settings.api_key = original


def test_requires_x_api_key_when_api_key_is_set() -> None:
    original = settings.api_key
    settings.api_key = 'test-secret'
    try:
        with TestClient(app) as client:
            unauthorized = client.get('/not-found')
            assert unauthorized.status_code == 401

            authorized = client.get('/not-found', headers={'X-API-Key': 'test-secret'})
            assert authorized.status_code == 404

            healthz = client.get('/healthz')
            assert healthz.status_code == 200
    finally:
        settings.api_key = original
