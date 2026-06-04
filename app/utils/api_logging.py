from fastapi import Request


def request_log_extra(request: Request, endpoint: str, **kwargs) -> dict:
    extra = {
        "request_id": getattr(request.state, "request_id", None),
        "user_id": getattr(request.state, "user_id", "unknown"),
        "path": request.url.path,
        "method": request.method,
        "endpoint": endpoint,
    }
    extra.update(kwargs)
    return extra
