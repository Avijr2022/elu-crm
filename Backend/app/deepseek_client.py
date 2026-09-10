"""DeepSeek V4 Flash client helper

Minimal wrapper using `httpx.Client` (already in requirements).
Reads the API key from the `DEEPSEEK_API_KEY` environment variable.

Usage:
    from app.deepseek_client import DeepSeekClient
    c = DeepSeekClient()
    if c.has_api_key():
        r = c.generate("Write a short email", max_tokens=50)
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx

DEFAULT_API_BASE = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-v4-flash"


class DeepSeekClient:
    def __init__(self, *, api_key: Optional[str] = None, api_base: Optional[str] = None, model: Optional[str] = None, timeout: int = 10):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.api_base = api_base or os.getenv("DEEPSEEK_API_BASE", DEFAULT_API_BASE)
        self.model = model or os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL)
        self._client = httpx.Client(timeout=timeout)
        if self.api_key:
            self._client.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            })

    def has_api_key(self) -> bool:
        """Return True if an API key is available in the client or environment."""
        return bool(self.api_key)

    def generate(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 200) -> Dict[str, Any]:
        """Send a generation request to DeepSeek and return parsed JSON.

        This method raises `httpx.HTTPStatusError` on non-2xx responses.
        Keep `max_tokens` small for quick checks to reduce token usage.
        """
        if not self.has_api_key():
            raise RuntimeError("DEEPSEEK_API_KEY environment variable is not set")

        payload = {"model": self.model, "input": prompt, "temperature": temperature, "max_tokens": max_tokens}
        url = f"{self.api_base}/responses"
        r = self._client.post(url, json=payload)
        r.raise_for_status()
        return r.json()


__all__ = ["DeepSeekClient"]
