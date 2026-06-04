import threading
import time
from typing import Any

from app.repositories.redis_repository import get_redis_client, json_dumps, json_loads


class TTLCacheRepository:
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        redis_client = get_redis_client()
        if redis_client is not None:
            raw = redis_client.get(key)
            if raw is None:
                return None
            return json_loads(raw)

        now = time.time()
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            expires_at, payload = item
            if expires_at < now:
                self._store.pop(key, None)
                return None
            return payload

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        redis_client = get_redis_client()
        if redis_client is not None:
            redis_client.setex(key, ttl_seconds, json_dumps(value))
            return

        expires_at = time.time() + ttl_seconds
        with self._lock:
            self._store[key] = (expires_at, value)


cache_repository = TTLCacheRepository()
