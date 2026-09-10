"""End-to-end check: login with seed admin and update tenant branding color.

Reads credentials from app settings (no hard-coded secrets here).
Targets a locally running backend on http://localhost:8000.
"""
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings

BASE = "http://localhost:8000"
COLOR = "#FF8F00"


def main() -> None:
    settings = get_settings()

    with httpx.Client(base_url=BASE, timeout=30) as c:
        login = c.post(
            "/api/v1/auth/login",
            json={
                "email": settings.seed_admin_email,
                "password": settings.seed_admin_password,
                "tenant_code": "EIIP001",
            },
        )
        print("login:", login.status_code)
        if login.status_code != 200:
            print(login.text)
            return
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        put = c.put(
            "/api/v1/tenant/branding/primary-color",
            headers=headers,
            json={"primary_color": COLOR},
        )
        print("branding PUT:", put.status_code)
        if put.status_code != 200:
            print(put.text)
            return
        body = put.json()
        print("tenant_id:", body.get("tenant_id"))
        print("primary_color:", body.get("primary_color"))
        print("E2E_BRANDING_OK" if body.get("primary_color") == COLOR else "E2E_BRANDING_MISMATCH")


if __name__ == "__main__":
    main()
