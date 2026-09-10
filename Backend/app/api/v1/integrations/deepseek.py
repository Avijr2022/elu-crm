from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import logging

from app.deepseek_client import DeepSeekClient
from app.core.deps import CurrentUser, get_current_user
from app.utils.redis_rate_limiter import (
    get_redis_client,
    increment_usage,
    rate_allowed_or_fail_open,
)

router = APIRouter(prefix="/integrations/deepseek", tags=["Integrations"])

logger = logging.getLogger(__name__)

# Distributed limiter defaults
RATE_LIMIT_PER_MINUTE = 600
PER_TENANT_TOKENS_PER_DAY = 10000


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    temperature: Optional[float] = Field(0.2, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(50, ge=1, le=512)


class GenerateResponse(BaseModel):
    response: dict


@router.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest, current: CurrentUser = Depends(get_current_user)):
    # Basic guards
    if req.max_tokens > 300:
        raise HTTPException(status_code=400, detail="max_tokens too large; limit 300")

    client = DeepSeekClient()
    if not client.has_api_key():
        raise HTTPException(status_code=503, detail="DeepSeek API key not configured")

    # Redis-backed rate limiting (graceful degradation when Redis is down)
    import os

    redis_url = os.getenv("REDIS_URL")
    r = None
    try:
        r = get_redis_client(redis_url)
        r.ping()
    except Exception:
        logger.warning("Redis unavailable at %s; rate limiting disabled for this request", redis_url)
        r = None

    # Global rate limit per minute
    if not rate_allowed_or_fail_open(r, "deepseek:global:minute", RATE_LIMIT_PER_MINUTE, period=60):
        raise HTTPException(status_code=429, detail="Global rate limit exceeded")

    # Per-tenant rate limit key
    tenant_minute_key = f"deepseek:tenant:{current.tenant_id}:minute"
    if not rate_allowed_or_fail_open(
        r, tenant_minute_key, int(RATE_LIMIT_PER_MINUTE / 10), period=60
    ):
        raise HTTPException(status_code=429, detail="Tenant rate limit exceeded")

    # Proceed to call upstream
    try:
        resp = client.generate(req.prompt, temperature=req.temperature, max_tokens=req.max_tokens)
    except Exception as exc:
        logger.exception("DeepSeek upstream error")
        raise HTTPException(status_code=502, detail=f"Upstream error: {exc}")

    # Log and record token usage if present (best effort)
    usage = resp.get("usage") or {}
    total_tokens = usage.get("total_tokens") or 0
    if total_tokens and r is not None:
        try:
            increment_usage(r, str(current.tenant_id), int(total_tokens))
        except Exception:
            logger.exception("Failed to record token usage in Redis")

    logger.info("DeepSeek request tenant=%s user=%s tokens=%s", current.tenant_id, current.user_id, total_tokens)
    return GenerateResponse(response=resp)
