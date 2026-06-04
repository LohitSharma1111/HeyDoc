import logging

from fastapi import APIRouter, Depends, Request

from app.core.config import Settings, get_settings
from app.schemas.auth_schema import TokenRequest, TokenResponse
from app.schemas.common_schema import ApiResponse
from app.services.auth_service import AuthService
from app.utils.api_logging import request_log_extra


router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/token", response_model=ApiResponse)
async def get_access_token(
    payload: TokenRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
):
    logger.info(
        "auth_token_requested",
        extra=request_log_extra(request, "auth.token"),
    )
    service = AuthService(settings)
    token_data = service.issue_token(payload.username, payload.password)
    logger.info(
        "auth_token_issued",
        extra=request_log_extra(
            request,
            "auth.token",
            status_code=200,
        ),
    )
    return ApiResponse(data=TokenResponse(**token_data))
