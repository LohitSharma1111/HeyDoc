import threading
import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

from app.core.config import get_settings
from app.repositories.redis_repository import get_redis_client


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._bucket: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.time()
        cutoff = now - window_seconds
        with self._lock:
            existing = [ts for ts in self._bucket[key] if ts >= cutoff]
            if len(existing) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please retry shortly.",
                )
            existing.append(now)
            self._bucket[key] = existing


rate_limiter = InMemoryRateLimiter()


async def enforce_rate_limit(request: Request) -> None:
    settings = get_settings()
    client = request.client.host if request.client else "unknown"
    redis_client = get_redis_client()
    if redis_client is not None:
        window = max(1, int(settings.rate_limit_window_seconds))
        bucket = int(time.time() // window)
        key = f"ratelimit:{client}:{bucket}"
        count = redis_client.incr(key)
        if count == 1:
            redis_client.expire(key, window)
        if count > settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please retry shortly.",
            )
        return

    rate_limiter.check(client, settings.rate_limit_per_minute, max(1, settings.rate_limit_window_seconds))
