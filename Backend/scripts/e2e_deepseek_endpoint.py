"""Live check: DeepSeek integration endpoint via the running backend.

Logs in with the seed admin and POSTs a minimal generation (max_tokens=1) to
/api/v1/integrations/deepseek/generate to confirm the server path uses the
configured DEEPSEEK_API_KEY. No key is stored here.
"""
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings  # noqa: E402

BASE = "http://localhost:8000"
API = f"{BASE}/api/v1"


def main() -> int:
    settings = get_settings()
    with httpx.Client(base_url=BASE, timeout=60) as c:
        login = c.post(
            f"{API}/auth/login",
            json={
                "email": settings.seed_admin_email,
                "password": settings.seed_admin_password,
                "tenant_code": "EIIP001",
            },
        )
        assert login.status_code == 200, login.text
        h = {"Authorization": f"Bearer {login.json()['access_token']}"}

        resp = c.post(
            f"{API}/integrations/deepseek/generate",
            headers=h,
            json={"prompt": "ping", "temperature": 0.0, "max_tokens": 1},
        )
        print("generate:", resp.status_code)
        if resp.status_code != 200:
            print(resp.text)
            return 1
        body = resp.json().get("response", {})
        print("model:", body.get("model"))
        print("status:", body.get("status"))
        print("usage:", body.get("usage"))
        print("E2E_DEEPSEEK_ENDPOINT_OK" if body.get("status") == "completed" else "UNEXPECTED")
        return 0 if body.get("status") == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
