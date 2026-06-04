import base64
import json
from typing import Any


def to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def from_base64(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))


def try_parse_json(text: str) -> Any:
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)

