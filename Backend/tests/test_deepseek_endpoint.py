"""Optional DeepSeek endpoint integration test.

Skipped by default to avoid API token spend. Enable explicitly:

    DEEPSEEK_E2E=1 DEEPSEEK_API_KEY=... python -m pytest tests/test_deepseek_endpoint.py

In CI, run the manual `workflow_dispatch` with `deepseek_smoke=true`.
"""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from app.models.pf import User
from tests.conftest import platform_session

pytestmark = pytest.mark.skipif(
    os.getenv("DEEPSEEK_E2E") != "1" or not os.getenv("DEEPSEEK_API_KEY"),
    reason="set DEEPSEEK_E2E=1 and DEEPSEEK_API_KEY to run the DeepSeek endpoint test",
)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(
            select(User).where(User.email == settings.seed_admin_email.lower())
        ).first()
        assert admin is not None
        admin.password_hash = hash_password(settings.seed_admin_password)
        db.commit()
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": settings.seed_admin_email,
            "password": settings.seed_admin_password,
            "tenant_code": "EIIP001",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_deepseek_generate_endpoint(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.post(
        "/api/v1/integrations/deepseek/generate",
        headers=headers,
        json={"prompt": "ping", "temperature": 0.0, "max_tokens": 1},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()["response"]
    assert body.get("status") == "completed"
    assert body.get("model")
