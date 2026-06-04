import datetime as dt
import threading
from collections import deque
from typing import Any

from app.repositories.redis_repository import get_redis_client, json_dumps, json_loads


AUDIT_LIST_KEY = "audit:events"


class AuditRepository:
    def __init__(self, max_items: int = 5000) -> None:
        self._events = deque(maxlen=max_items)
        self._lock = threading.Lock()

    def append(self, action: str, details: dict[str, Any]) -> None:
        event = {
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "action": action,
            "details": details,
        }

        redis_client = get_redis_client()
        if redis_client is not None:
            redis_client.rpush(AUDIT_LIST_KEY, json_dumps(event))
            redis_client.ltrim(AUDIT_LIST_KEY, -self._events.maxlen, -1)
            return

        with self._lock:
            self._events.append(event)

    def list_recent(self, limit: int = 100) -> list[dict[str, Any]]:
        redis_client = get_redis_client()
        if redis_client is not None:
            raw_items = redis_client.lrange(AUDIT_LIST_KEY, -limit, -1)
            return [json_loads(item) for item in raw_items]

        with self._lock:
            return list(self._events)[-limit:]


audit_repository = AuditRepository()
