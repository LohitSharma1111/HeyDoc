import asyncio
import logging
from typing import Any

from app.core.config import get_settings
from app.schemas.job_schema import JOB_PAYLOAD_MODELS
from app.services.ai_service import AIService
from app.services.delivery_service import DeliveryService
from app.services.note_service import NoteService
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _validate_payload(job_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    model = JOB_PAYLOAD_MODELS[job_type]
    validated = model.model_validate(payload)
    return validated.model_dump()


def _run(coro):
    return asyncio.run(coro)


@celery_app.task(name="jobs.run", bind=True)
def run_job(self, job_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    logger.info(
        "job_worker_started",
        extra={
            "job_id": self.request.id,
            "job_type": job_type,
        },
    )
    valid_types = set(JOB_PAYLOAD_MODELS.keys())
    if job_type not in valid_types:
        logger.warning(
            "job_worker_invalid_job_type",
            extra={"job_id": self.request.id, "job_type": job_type},
        )
        raise ValueError("Unsupported job type")
    valid_type = job_type
    data = _validate_payload(valid_type, payload)

    if valid_type == "notes.generate":
        service = NoteService(settings)
        output = _run(
            service.run_pipeline(
                transcript_text=data.get("transcript_text", ""),
                audio_base64=data.get("audio_base64", ""),
                audio_segments_base64=data.get("audio_segments_base64"),
                recording_paused=bool(data.get("recording_paused", False)),
                include_pdf_base64=bool(data.get("include_pdf_base64", True)),
            )
        )
        logger.info("job_worker_succeeded", extra={"job_id": self.request.id, "job_type": job_type})
        return output

    if valid_type == "notes.regenerate":
        service = NoteService(settings)
        output = _run(
            service.regenerate_note(
                raw_text=data.get("raw_text", ""),
                diarized_text=data.get("diarized_text", ""),
                include_pdf_base64=bool(data.get("include_pdf_base64", True)),
            )
        )
        logger.info("job_worker_succeeded", extra={"job_id": self.request.id, "job_type": job_type})
        return output

    ai_service = AIService(settings)
    if valid_type == "notes.issues":
        output = _run(ai_service.detect_transcript_issues(data["raw_text"], data["diarized_text"]))
        logger.info("job_worker_succeeded", extra={"job_id": self.request.id, "job_type": job_type})
        return output

    if valid_type == "notes.icd10":
        soap = data["soap"]
        output = _run(ai_service.suggest_icd10(soap))
        logger.info("job_worker_succeeded", extra={"job_id": self.request.id, "job_type": job_type})
        return output

    if valid_type == "notes.followup_reminder":
        soap = data["soap"]
        reminder = _run(ai_service.generate_followup_reminder(soap))
        output = {"message": reminder}
        logger.info("job_worker_succeeded", extra={"job_id": self.request.id, "job_type": job_type})
        return output

    if valid_type == "notes.send":
        service = DeliveryService(settings)
        output = _run(
            service.send(
                channel=data["channel"],
                pdf_base64=data.get("pdf_base64", ""),
                recipient=data.get("recipient", ""),
                fax_number=data.get("fax_number", ""),
                fallback_email=data.get("fallback_email", ""),
                to_email=data.get("to_email", ""),
                subject=data.get("subject"),
                body=data.get("body"),
                attach_pdf=bool(data.get("attach_pdf", True)),
                attachment_name=data.get("attachment_name"),
                provider_tag=data.get("provider_tag", "email"),
                retries=data.get("retries"),
                retry_delay_seconds=data.get("retry_delay_seconds"),
            )
        )
        logger.info("job_worker_succeeded", extra={"job_id": self.request.id, "job_type": job_type})
        return output

    logger.warning("job_worker_invalid_job_type", extra={"job_id": self.request.id, "job_type": job_type})
    raise ValueError("Unsupported job type")
