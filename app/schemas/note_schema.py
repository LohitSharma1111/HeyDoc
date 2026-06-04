from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SubjectiveSchema(BaseModel):
    chief_complaint: str = "Not documented"
    history_of_present_illness: str = "Not documented"
    symptoms: list[str] = Field(default_factory=list)
    duration: str = "Not documented"
    severity: str = "Not documented"


class ObjectiveSchema(BaseModel):
    vitals: str = "Not documented"
    physical_exam: str = "Not documented"
    observations: list[str] = Field(default_factory=list)


class AssessmentSchema(BaseModel):
    diagnosis: str = "Not documented"
    differential: list[str] = Field(default_factory=list)


class PlanSchema(BaseModel):
    investigations: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    follow_up: str = "Not documented"
    instructions: str = "Not documented"


class SoapSchema(BaseModel):
    subjective: SubjectiveSchema = Field(default_factory=SubjectiveSchema)
    objective: ObjectiveSchema = Field(default_factory=ObjectiveSchema)
    assessment: AssessmentSchema = Field(default_factory=AssessmentSchema)
    plan: PlanSchema = Field(default_factory=PlanSchema)


class GenerateNoteRequest(BaseModel):
    transcript_text: str = ""
    audio_base64: str = ""
    audio_segments_base64: list[str] = Field(default_factory=list)
    recording_paused: bool = False
    include_pdf_base64: bool = True

    @field_validator("transcript_text", mode="before")
    @classmethod
    def normalize_transcript(cls, value: str) -> str:
        return (value or "").strip()

    @field_validator("audio_segments_base64", mode="before")
    @classmethod
    def normalize_audio_segments(cls, value):
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("audio_segments_base64 must be a list of base64 WAV chunks.")
        return [str(item).strip() for item in value if str(item or "").strip()]


class GenerateNoteResponse(BaseModel):
    transcript: str
    diarized_transcript: str
    soap_markdown: str
    patient_summary: str
    soap: SoapSchema
    pdf_base64: str | None = None


class RegenerateNoteRequest(BaseModel):
    raw_text: str = ""
    diarized_text: str = ""
    include_pdf_base64: bool = True


class TranscriptIssueSchema(BaseModel):
    issue: str
    suggestion: str
    severity: Literal["high", "medium", "low"]


class DetectIssuesRequest(BaseModel):
    raw_text: str = Field(min_length=1)
    diarized_text: str = Field(min_length=1)


class ICD10Item(BaseModel):
    code: str
    description: str
    confidence: Literal["high", "medium", "low"]


class ICD10Request(BaseModel):
    soap: SoapSchema


class ReminderRequest(BaseModel):
    soap: SoapSchema


class SendNoteRequest(BaseModel):
    pdf_base64: str = ""
    channel: Literal["mock", "email", "kno2", "fax_kno2", "fax_auto", "srfax", "phaxio"] = "mock"
    recipient: str = ""
    fax_number: str = ""
    fallback_email: str = ""
    to_email: str = ""
    subject: str | None = None
    body: str | None = None
    attach_pdf: bool = True
    attachment_name: str | None = None
    provider_tag: str = "email"
    retries: int | None = None
    retry_delay_seconds: float | None = None
