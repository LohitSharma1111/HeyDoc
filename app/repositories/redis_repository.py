import json
import logging
from typing import Any

import redis

from app.core.config import get_settings


logger = logging.getLogger(__name__)
_redis_client: redis.Redis | None = None
_redis_failed = False


def get_redis_client() -> redis.Redis | None:
    global _redis_client, _redis_failed
    if _redis_client is not None:
        return _redis_client
    if _redis_failed:
        return None

    settings = get_settings()
    try:
        client = redis.from_url(settings.redis_url, decode_responses=True)
        client.ping()
        _redis_client = client
        return _redis_client
    except Exception as exc:
        _redis_failed = True
        logger.warning("redis_unavailable: %s", exc)
        return None


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True)


def json_loads(value: str) -> Any:
    return json.loads(value)
