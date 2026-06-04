import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.dependencies import enforce_rate_limit
from app.core.security import Principal, get_current_principal
from app.schemas.common_schema import ApiResponse
from app.schemas.job_schema import EnqueueJobRequest, EnqueueJobResponse, JobStatusResponse
from app.services.job_service import JobService
from app.utils.api_logging import request_log_extra


router = APIRouter(prefix="/jobs", tags=["jobs"])
logger = logging.getLogger(__name__)


@router.post("", response_model=ApiResponse, dependencies=[Depends(enforce_rate_limit)])
async def enqueue_job(
    payload: EnqueueJobRequest,
    request: Request,
    _principal: Principal = Depends(get_current_principal),
):
    logger.info(
        "jobs_enqueue_requested",
        extra=request_log_extra(request, "jobs.enqueue", job_type=payload.job_type),
    )
    try:
        job_id = JobService.enqueue(payload.job_type, payload.payload)
    except ValueError as exc:
        logger.warning(
            "jobs_enqueue_validation_failed",
            extra=request_log_extra(request, "jobs.enqueue", status_code=400, job_type=payload.job_type, error=str(exc)),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception(
            "jobs_enqueue_failed",
            exc_info=exc,
            extra=request_log_extra(request, "jobs.enqueue", status_code=503, job_type=payload.job_type),
        )
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Queue unavailable.") from exc

    logger.info(
        "jobs_enqueue_succeeded",
        extra=request_log_extra(request, "jobs.enqueue", status_code=200, job_type=payload.job_type, job_id=job_id),
    )
    return ApiResponse(data=EnqueueJobResponse(job_id=job_id, job_type=payload.job_type))


@router.get("/{job_id}", response_model=ApiResponse, dependencies=[Depends(enforce_rate_limit)])
async def get_job_status(
    job_id: str,
    request: Request,
    _principal: Principal = Depends(get_current_principal),
):
    logger.info(
        "jobs_status_requested",
        extra=request_log_extra(request, "jobs.status", job_id=job_id),
    )
    status_payload = JobService.get_status(job_id)
    logger.info(
        "jobs_status_succeeded",
        extra=request_log_extra(
            request,
            "jobs.status",
            status_code=200,
            job_id=job_id,
            job_type=status_payload.get("job_type"),
        ),
    )
    return ApiResponse(data=JobStatusResponse(**status_payload))
