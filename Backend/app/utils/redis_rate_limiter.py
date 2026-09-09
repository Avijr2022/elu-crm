from __future__ import annotations

import logging
from typing import Optional

import redis

logger = logging.getLogger(__name__)


def get_redis_client(url: Optional[str] = None) -> redis.Redis:
    url = url or "redis://localhost:6379/0"
    return redis.from_url(
        url,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )


def check_and_increment_rate(redis_client: redis.Redis, key: str, limit: int, period: int = 60) -> bool:
    """Atomically increment a counter and return True if under limit.

    Uses INCR and EXPIRE to implement a sliding fixed window.
    """
    p = redis_client.pipeline()
    p.incr(key, amount=1)
    p.ttl(key)
    val, ttl = p.execute()
    if ttl == -1:
        redis_client.expire(key, period)
    logger.debug("Rate key=%s value=%s ttl=%s", key, val, ttl)
    return int(val) <= int(limit)


def rate_allowed_or_fail_open(
    redis_client: Optional[redis.Redis], key: str, limit: int, period: int = 60
) -> bool:
    """Rate-limit check that fails OPEN when Redis is unavailable.

    Returns True (allow) if `redis_client` is None or raises on the operation,
    logging a warning so the limiter never crashes the request path. When Redis
    is reachable it delegates to `check_and_increment_rate`.
    """
    if redis_client is None:
        logger.warning("Redis unavailable for key=%s; allowing request (fail-open)", key)
        return True
    try:
        return check_and_increment_rate(redis_client, key, limit, period)
    except redis.RedisError:
        logger.warning("Redis error on key=%s; allowing request (fail-open)", key, exc_info=True)
        return True


def increment_usage(redis_client: redis.Redis, tenant_key: str, tokens: int) -> None:
    """Increment token usage counter for tenant (daily granularity)."""
    field = tenant_key
    # store daily key
    from datetime import datetime

    day = datetime.utcnow().strftime("%Y-%m-%d")
    redis_key = f"deepseek:usage:{day}"
    redis_client.hincrby(redis_key, field, tokens)
    # keep 30 days
    redis_client.expire(redis_key, 60 * 60 * 24 * 30)
