from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.note_schema import (
    DetectIssuesRequest,
    GenerateNoteRequest,
    ICD10Request,
    RegenerateNoteRequest,
    ReminderRequest,
    SendNoteRequest,
)


JobType = Literal[
    "notes.generate",
    "notes.regenerate",
    "notes.issues",
    "notes.icd10",
    "notes.followup_reminder",
    "notes.send",
]

JobStatus = Literal["queued", "started", "success", "failed", "unknown"]


class EnqueueJobRequest(BaseModel):
    job_type: JobType
    payload: dict[str, Any] = Field(default_factory=dict)


class EnqueueJobResponse(BaseModel):
    job_id: str
    job_type: JobType
    status: JobStatus = "queued"


class JobStatusResponse(BaseModel):
    job_id: str
    job_type: str | None = None
    status: JobStatus
    result: Any | None = None
    error: str | None = None


JOB_PAYLOAD_MODELS: dict[JobType, type[BaseModel]] = {
    "notes.generate": GenerateNoteRequest,
    "notes.regenerate": RegenerateNoteRequest,
    "notes.issues": DetectIssuesRequest,
    "notes.icd10": ICD10Request,
    "notes.followup_reminder": ReminderRequest,
    "notes.send": SendNoteRequest,
}
