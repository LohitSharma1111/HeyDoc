from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    status: str = "success"
    data: Any


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    request_id: str | None = None

