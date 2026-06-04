import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.config import Settings, get_settings
from app.core.dependencies import enforce_rate_limit
from app.core.security import Principal, get_current_principal
from app.repositories.audit_repository import audit_repository
from app.schemas.common_schema import ApiResponse
from app.schemas.note_schema import (
    DetectIssuesRequest,
    GenerateNoteRequest,
    GenerateNoteResponse,
    ICD10Request,
    ICD10Item,
    RegenerateNoteRequest,
    ReminderRequest,
    SendNoteRequest,
    TranscriptIssueSchema,
)
from app.services.ai_service import AIService
from app.services.delivery_service import DeliveryService
from app.services.note_service import NoteService
from app.utils.api_logging import request_log_extra


router = APIRouter(prefix="/notes", tags=["notes"])
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=ApiResponse, dependencies=[Depends(enforce_rate_limit)])
async def generate_note(
    payload: GenerateNoteRequest,
    request: Request,
    _principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_settings),
):
    logger.info(
        "notes_generate_requested",
        extra=request_log_extra(
            request,
            "notes.generate",
            channel="n/a",
        ),
    )
    service = NoteService(settings)
    try:
        result = await service.run_pipeline(
            transcript_text=payload.transcript_text,
            audio_base64=payload.audio_base64,
            audio_segments_base64=payload.audio_segments_base64,
            recording_paused=payload.recording_paused,
            include_pdf_base64=payload.include_pdf_base64,
        )
    except ValueError as exc:
        logger.warning(
            "notes_generate_validation_failed",
            extra=request_log_extra(request, "notes.generate", status_code=400, error=str(exc)),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    audit_repository.append(
        "NOTE_GENERATED",
        {
            "request_id": getattr(request.state, "request_id", ""),
            "user_id": getattr(request.state, "user_id", "anonymous"),
        },
    )
    logger.info(
        "notes_generate_succeeded",
        extra=request_log_extra(
            request,
            "notes.generate",
            status_code=200,
        ),
    )
    return ApiResponse(data=GenerateNoteResponse(**result))


@router.post("/regenerate", response_model=ApiResponse, dependencies=[Depends(enforce_rate_limit)])
async def regenerate_note(
    payload: RegenerateNoteRequest,
    request: Request,
    _principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_settings),
):
    logger.info(
        "notes_regenerate_requested",
        extra=request_log_extra(request, "notes.regenerate"),
    )
    service = NoteService(settings)
    try:
        result = await service.regenerate_note(
            raw_text=payload.raw_text,
            diarized_text=payload.diarized_text,
            include_pdf_base64=payload.include_pdf_base64,
        )
    except ValueError as exc:
        logger.warning(
            "notes_regenerate_validation_failed",
            extra=request_log_extra(request, "notes.regenerate", status_code=400, error=str(exc)),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    logger.info(
        "notes_regenerate_succeeded",
        extra=request_log_extra(request, "notes.regenerate", status_code=200),
    )
    return ApiResponse(data=GenerateNoteResponse(**result))


@router.post("/issues", response_model=ApiResponse, dependencies=[Depends(enforce_rate_limit)])
async def detect_issues(
    payload: DetectIssuesRequest,
    request: Request,
    _principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_settings),
):
    logger.info(
        "notes_issues_requested",
        extra=request_log_extra(
            request,
            "notes.issues",
        ),
    )
    ai_service = AIService(settings)
    issues = await ai_service.detect_transcript_issues(payload.raw_text, payload.diarized_text)
    data = [TranscriptIssueSchema(**item) for item in issues if isinstance(item, dict)]
    logger.info(
        "notes_issues_succeeded",
        extra=request_log_extra(request, "notes.issues", status_code=200, result_count=len(data)),
    )
    return ApiResponse(data=data)


@router.post("/icd10", response_model=ApiResponse, dependencies=[Depends(enforce_rate_limit)])
async def suggest_icd10(
    payload: ICD10Request,
    request: Request,
    _principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_settings),
):
    logger.info(
        "notes_icd10_requested",
        extra=request_log_extra(request, "notes.icd10"),
    )
    ai_service = AIService(settings)
    result = await ai_service.suggest_icd10(payload.soap.model_dump())
    data = [ICD10Item(**item) for item in result if isinstance(item, dict)]
    logger.info(
        "notes_icd10_succeeded",
        extra=request_log_extra(request, "notes.icd10", status_code=200, result_count=len(data)),
    )
    return ApiResponse(data=data)


@router.post("/followup-reminder", response_model=ApiResponse, dependencies=[Depends(enforce_rate_limit)])
async def followup_reminder(
    payload: ReminderRequest,
    request: Request,
    _principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_settings),
):
    logger.info(
        "notes_followup_requested",
        extra=request_log_extra(request, "notes.followup_reminder"),
    )
    ai_service = AIService(settings)
    reminder = await ai_service.generate_followup_reminder(payload.soap.model_dump())
    logger.info(
        "notes_followup_succeeded",
        extra=request_log_extra(request, "notes.followup_reminder", status_code=200),
    )
    return ApiResponse(data={"message": reminder})


@router.post("/send", response_model=ApiResponse, dependencies=[Depends(enforce_rate_limit)])
async def send_note(
    payload: SendNoteRequest,
    request: Request,
    _principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_settings),
):
    logger.info(
        "notes_send_requested",
        extra=request_log_extra(request, "notes.send", channel=payload.channel),
    )
    service = DeliveryService(settings)
    send_result = await service.send(
        channel=payload.channel,
        pdf_base64=payload.pdf_base64,
        recipient=payload.recipient,
        fax_number=payload.fax_number,
        fallback_email=payload.fallback_email,
        to_email=payload.to_email,
        subject=payload.subject,
        body=payload.body,
        attach_pdf=payload.attach_pdf,
        attachment_name=payload.attachment_name,
        provider_tag=payload.provider_tag,
        retries=payload.retries,
        retry_delay_seconds=payload.retry_delay_seconds,
    )
    audit_repository.append(
        "NOTE_SENT",
        {
            "request_id": getattr(request.state, "request_id", ""),
            "user_id": getattr(request.state, "user_id", "anonymous"),
            "channel": payload.channel,
            "provider": send_result.get("provider"),
            "message_id": send_result.get("message_id"),
            "attempts": send_result.get("attempts"),
            "status": "success" if send_result.get("success") else "failed",
        },
    )
    logger.info(
        "notes_send_completed",
        extra=request_log_extra(
            request,
            "notes.send",
            status_code=200,
            channel=payload.channel,
        ),
    )
    return ApiResponse(data=send_result)


@router.get("/audit", response_model=ApiResponse, dependencies=[Depends(enforce_rate_limit)])
async def audit_events(
    request: Request,
    limit: int = 50,
    _principal: Principal = Depends(get_current_principal),
):
    safe_limit = min(max(limit, 1), 500)
    logger.info(
        "notes_audit_requested",
        extra=request_log_extra(request, "notes.audit", limit=safe_limit),
    )
    events = audit_repository.list_recent(limit=safe_limit)
    logger.info(
        "notes_audit_succeeded",
        extra=request_log_extra(request, "notes.audit", status_code=200, result_count=len(events), limit=safe_limit),
    )
    return ApiResponse(data=events)
