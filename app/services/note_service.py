import asyncio
import io
import wave

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.core.config import Settings
from app.schemas.note_schema import SoapSchema
from app.services.ai_service import AIService
from app.utils.helpers import from_base64, to_base64


class NoteService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ai_service = AIService(settings)

    async def run_pipeline(
        self,
        transcript_text: str,
        audio_base64: str,
        audio_segments_base64: list[str] | None = None,
        recording_paused: bool = False,
        include_pdf_base64: bool = True,
    ) -> dict:
        transcript = transcript_text.strip()
        audio_chunks: list[bytes] = []
        if audio_base64:
            audio_chunks.append(from_base64(audio_base64))
        for item in (audio_segments_base64 or []):
            audio_chunks.append(from_base64(item))

        if recording_paused and not audio_chunks and not transcript:
            raise ValueError("Recording is paused. Resume recording or provide transcript/audio before generating.")

        if audio_chunks:
            audio_bytes = self.merge_wav_chunks(audio_chunks)
            max_bytes = self.settings.max_audio_mb * 1024 * 1024
            if len(audio_bytes) > max_bytes:
                raise ValueError(f"Audio exceeds {self.settings.max_audio_mb} MB limit.")
            transcript = await self.ai_service.transcribe_audio(audio_bytes)

        if not transcript:
            raise ValueError("Provide transcript_text or audio_base64.")

        diarized = await self.ai_service.diarize_transcript(transcript)
        soap = await self.ai_service.generate_soap(diarized)
        soap_model = SoapSchema.model_validate(soap)
        summary = await self.ai_service.generate_patient_summary(soap_model.model_dump())
        soap_md = self.format_soap_markdown(soap_model.model_dump())

        pdf_base64 = None
        if include_pdf_base64:
            pdf_bytes = await asyncio.to_thread(self.create_soap_pdf_bytes, soap_model.model_dump())
            pdf_base64 = to_base64(pdf_bytes)

        return {
            "transcript": transcript,
            "diarized_transcript": diarized,
            "soap_markdown": soap_md,
            "patient_summary": summary,
            "soap": soap_model.model_dump(),
            "pdf_base64": pdf_base64,
        }

    @staticmethod
    def merge_wav_chunks(audio_chunks: list[bytes]) -> bytes:
        chunks = [chunk for chunk in audio_chunks if chunk]
        if not chunks:
            return b""
        if len(chunks) == 1:
            return chunks[0]

        collected_frames: list[bytes] = []
        output_format = None
        for idx, chunk in enumerate(chunks):
            try:
                with wave.open(io.BytesIO(chunk), "rb") as wav_in:
                    chunk_format = (
                        wav_in.getnchannels(),
                        wav_in.getsampwidth(),
                        wav_in.getframerate(),
                        wav_in.getcomptype(),
                        wav_in.getcompname(),
                    )
                    if output_format is None:
                        output_format = chunk_format
                    elif chunk_format != output_format:
                        raise ValueError("Audio chunk format mismatch. Ensure all chunks use the same recording settings.")
                    collected_frames.append(wav_in.readframes(wav_in.getnframes()))
            except wave.Error as exc:
                raise ValueError(f"Invalid WAV audio chunk at index {idx}.") from exc

        out = io.BytesIO()
        with wave.open(out, "wb") as wav_out:
            wav_out.setnchannels(output_format[0])
            wav_out.setsampwidth(output_format[1])
            wav_out.setframerate(output_format[2])
            wav_out.setcomptype(output_format[3], output_format[4])
            wav_out.writeframes(b"".join(collected_frames))
        return out.getvalue()

    async def regenerate_note(
        self,
        raw_text: str,
        diarized_text: str,
        include_pdf_base64: bool = True,
    ) -> dict:
        raw = (raw_text or "").strip()
        diarized = (diarized_text or "").strip()
        if not diarized:
            if not raw:
                raise ValueError("Add corrected raw_text or diarized_text.")
            diarized = await self.ai_service.diarize_transcript(raw)

        soap = await self.ai_service.generate_soap(diarized)
        soap_model = SoapSchema.model_validate(soap)
        summary = await self.ai_service.generate_patient_summary(soap_model.model_dump())
        soap_md = self.format_soap_markdown(soap_model.model_dump())

        pdf_base64 = None
        if include_pdf_base64:
            pdf_bytes = await asyncio.to_thread(self.create_soap_pdf_bytes, soap_model.model_dump())
            pdf_base64 = to_base64(pdf_bytes)

        return {
            "transcript": raw,
            "diarized_transcript": diarized,
            "soap_markdown": soap_md,
            "patient_summary": summary,
            "soap": soap_model.model_dump(),
            "pdf_base64": pdf_base64,
        }

    @staticmethod
    def format_soap_markdown(soap: dict) -> str:
        s = soap.get("subjective", {})
        o = soap.get("objective", {})
        a = soap.get("assessment", {})
        p = soap.get("plan", {})

        def value(item):
            return str(item).strip() if item not in (None, "", []) else "Not documented"

        def bullets(items):
            if not items:
                return "- Not documented"
            return "\n".join(f"- {str(x).strip()}" for x in items if str(x).strip())

        return f"""## S — Subjective
**Chief Complaint:** {value(s.get('chief_complaint'))}
**History:** {value(s.get('history_of_present_illness'))}
**Duration:** {value(s.get('duration'))}  ·  **Severity:** {value(s.get('severity'))}
**Symptoms:**
{bullets(s.get('symptoms', []))}

## O — Objective
**Vitals:** {value(o.get('vitals'))}
**Examination:** {value(o.get('physical_exam'))}
**Observations:**
{bullets(o.get('observations', []))}

## A — Assessment
**Primary Diagnosis:** {value(a.get('diagnosis'))}
**Differential:**
{bullets(a.get('differential', []))}

## P — Plan
**Investigations:**
{bullets(p.get('investigations', []))}
**Medications:**
{bullets(p.get('medications', []))}
**Follow-Up:** {value(p.get('follow_up'))}
**Instructions:** {value(p.get('instructions'))}
"""

    @staticmethod
    def create_soap_pdf_bytes(soap: dict) -> bytes:
        styles = getSampleStyleSheet()
        title_style = styles["Heading2"]
        body_style = styles["BodyText"]
        body_style.leading = 14

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=letter,
            leftMargin=0.6 * inch,
            rightMargin=0.6 * inch,
            topMargin=0.8 * inch,
            bottomMargin=0.6 * inch,
            title="SOAP Note",
        )
        story = []

        def add_section(title: str, content: str) -> None:
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 6))
            story.append(Paragraph(content.replace("\n", "<br/>"), body_style))
            story.append(Spacer(1, 12))

        markdown = NoteService.format_soap_markdown(soap)
        sections = [part.strip() for part in markdown.split("## ") if part.strip()]
        for section in sections:
            first_line, _, rest = section.partition("\n")
            add_section(first_line, rest.strip())

        def add_footer(pdf_canvas: canvas.Canvas, _doc):
            pdf_canvas.saveState()
            pdf_canvas.setFillColor(colors.HexColor("#64748B"))
            pdf_canvas.setFont("Helvetica", 8)
            pdf_canvas.drawString(0.6 * inch, 0.35 * inch, "HeyDoc AI Medical Scribe")
            pdf_canvas.restoreState()

        doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
        return buf.getvalue()
