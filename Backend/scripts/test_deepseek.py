"""Small test runner for DeepSeek integration.

Checks for `DEEPSEEK_API_KEY` in the environment. If present, makes a minimal
generation call with `max_tokens=1` to verify token availability while
minimizing token usage.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.deepseek_client import DeepSeekClient


def main() -> int:
    client = DeepSeekClient()
    if not client.has_api_key():
        print("DEEPSEEK_API_KEY not found in environment. Skipping API call.")
        return 2

    try:
        print("DEEPSEEK_API_KEY found — running minimal API check (1 token)...")
        resp = client.generate("Token check", temperature=0.0, max_tokens=1)
        print("API call successful. Response summary:")
        print(resp)
        return 0
    except Exception as exc:  # keep broad to surface any connectivity/auth errors
        print("API call failed:", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
