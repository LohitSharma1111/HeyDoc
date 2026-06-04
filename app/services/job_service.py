from typing import Any

from celery.result import AsyncResult

from app.schemas.job_schema import JOB_PAYLOAD_MODELS, JobType
from app.workers.celery_app import celery_app


class JobService:
    @staticmethod
    def enqueue(job_type: JobType, payload: dict[str, Any]) -> str:
        model = JOB_PAYLOAD_MODELS[job_type]
        validated_payload = model.model_validate(payload).model_dump()
        task = celery_app.send_task("jobs.run", args=[job_type, validated_payload])
        return task.id

    @staticmethod
    def get_status(job_id: str) -> dict[str, Any]:
        result = AsyncResult(job_id, app=celery_app)
        state = (result.state or "").upper()
        mapped = {
            "PENDING": "queued",
            "RECEIVED": "queued",
            "RETRY": "queued",
            "STARTED": "started",
            "SUCCESS": "success",
            "FAILURE": "failed",
            "REVOKED": "failed",
        }.get(state, "unknown")

        payload: dict[str, Any] = {
            "job_id": job_id,
            "status": mapped,
        }

        if state == "SUCCESS":
            payload["result"] = result.result
        elif state == "FAILURE":
            payload["error"] = str(result.result)

        return payload
