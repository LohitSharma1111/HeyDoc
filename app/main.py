import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.middlewares.logging_middleware import RequestLoggingMiddleware
from app.schemas.common_schema import ErrorResponse
from app.utils.logger import setup_logging


settings = get_settings()
setup_logging(logging.DEBUG if settings.debug else logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=settings.gzip_minimum_size)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def healthcheck(request: Request):
    logger.info(
        "healthcheck_requested",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "user_id": getattr(request.state, "user_id", "unknown"),
            "path": request.url.path,
            "method": request.method,
            "endpoint": "health",
            "status_code": 200,
        },
    )
    return {"status": "ok", "service": settings.app_name, "env": settings.app_env}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logging.getLogger("app.error").warning(
        "http_exception",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "user_id": getattr(request.state, "user_id", "unknown"),
            "path": request.url.path,
            "method": request.method,
            "endpoint": "http_exception_handler",
            "status_code": exc.status_code,
            "error": str(exc.detail),
        },
    )
    payload = ErrorResponse(message=str(exc.detail), request_id=getattr(request.state, "request_id", None))
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.getLogger("app.error").exception(
        "unhandled_exception",
        exc_info=exc,
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "user_id": getattr(request.state, "user_id", "unknown"),
            "path": request.url.path,
            "method": request.method,
            "endpoint": "unhandled_exception_handler",
            "status_code": 500,
            "error": str(exc),
        },
    )
    payload = ErrorResponse(message="Internal server error", request_id=getattr(request.state, "request_id", None))
    return JSONResponse(status_code=500, content=payload.model_dump())
