"""Opportunity stage admin API tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from app.models.pf import User
from tests.conftest import platform_admin_select, platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(
            platform_admin_select()
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


def test_list_and_deactivate_opportunity_stage(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    listed = client.get(
        "/api/v1/crm/opportunity-stages?include_inactive=true",
        headers=headers,
    )
    assert listed.status_code == 200, listed.text
    items = listed.json()["items"]
    assert len(items) >= 6
    stage_id = items[0]["opportunity_stage_id"]

    patch = client.patch(
        f"/api/v1/crm/opportunity-stages/{stage_id}",
        headers=headers,
        json={"is_active": False},
    )
    assert patch.status_code == 200, patch.text
    assert patch.json()["is_active"] is False

    active_only = client.get("/api/v1/crm/opportunity-stages", headers=headers)
    active_codes = {i["code"] for i in active_only.json()["items"]}
    assert items[0]["code"] not in active_codes

    restore = client.patch(
        f"/api/v1/crm/opportunity-stages/{stage_id}",
        headers=headers,
        json={"is_active": True},
    )
    assert restore.status_code == 200, restore.text


def test_pipeline_uses_active_db_stages(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    listed = client.get("/api/v1/crm/opportunity-stages", headers=headers)
    assert listed.status_code == 200, listed.text
    active_codes = [i["code"] for i in listed.json()["items"]]
    assert len(active_codes) >= 6

    pipeline = client.get("/api/v1/crm/opportunities/pipeline", headers=headers)
    assert pipeline.status_code == 200, pipeline.text
    bucket_stages = [b["stage"] for b in pipeline.json()["stages"]]
    assert bucket_stages == active_codes

    stage_id = listed.json()["items"][0]["opportunity_stage_id"]
    deactivated_code = listed.json()["items"][0]["code"]
    patch = client.patch(
        f"/api/v1/crm/opportunity-stages/{stage_id}",
        headers=headers,
        json={"is_active": False},
    )
    assert patch.status_code == 200, patch.text

    pipeline2 = client.get("/api/v1/crm/opportunities/pipeline", headers=headers)
    assert pipeline2.status_code == 200, pipeline2.text
    bucket_stages2 = [b["stage"] for b in pipeline2.json()["stages"]]
    assert deactivated_code not in bucket_stages2
    assert len(bucket_stages2) == len(active_codes) - 1

    client.patch(
        f"/api/v1/crm/opportunity-stages/{stage_id}",
        headers=headers,
        json={"is_active": True},
    )


def test_reorder_opportunity_stages(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    listed = client.get(
        "/api/v1/crm/opportunity-stages?include_inactive=true",
        headers=headers,
    )
    assert listed.status_code == 200, listed.text
    items = listed.json()["items"]
    assert len(items) >= 2
    original_codes = [i["code"] for i in items]
    reversed_ids = [items[1]["opportunity_stage_id"], items[0]["opportunity_stage_id"]] + [
        i["opportunity_stage_id"] for i in items[2:]
    ]

    reorder = client.put(
        "/api/v1/crm/opportunity-stages/reorder",
        headers=headers,
        json={"stage_ids": reversed_ids},
    )
    assert reorder.status_code == 200, reorder.text

    listed2 = client.get(
        "/api/v1/crm/opportunity-stages?include_inactive=true",
        headers=headers,
    )
    assert listed2.status_code == 200, listed2.text
    new_codes = [i["code"] for i in listed2.json()["items"]]
    assert new_codes[0] == original_codes[1]
    assert new_codes[1] == original_codes[0]

    pipeline = client.get("/api/v1/crm/opportunities/pipeline", headers=headers)
    assert pipeline.status_code == 200, pipeline.text
    active_codes = [i["code"] for i in listed2.json()["items"] if i["is_active"]]
    bucket_stages = [b["stage"] for b in pipeline.json()["stages"]]
    assert bucket_stages == active_codes

    restore = client.put(
        "/api/v1/crm/opportunity-stages/reorder",
        headers=headers,
        json={"stage_ids": [i["opportunity_stage_id"] for i in items]},
    )
    assert restore.status_code == 200, restore.text


def test_create_opportunity_stage(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    code = f"CUSTOM{uuid.uuid4().hex[:4].upper()}"
    create = client.post(
        "/api/v1/crm/opportunity-stages",
        headers=headers,
        json={
            "code": code,
            "name": "Custom Review",
            "default_probability": 25,
        },
    )
    assert create.status_code == 201, create.text
    body = create.json()
    assert body["code"] == code
    assert body["default_probability"] == 25
    assert body["is_active"] is True

    listed = client.get("/api/v1/crm/opportunity-stages", headers=headers)
    assert listed.status_code == 200, listed.text
    assert code in {i["code"] for i in listed.json()["items"]}

    pipeline = client.get("/api/v1/crm/opportunities/pipeline", headers=headers)
    assert pipeline.status_code == 200, pipeline.text
    assert code in [b["stage"] for b in pipeline.json()["stages"]]
