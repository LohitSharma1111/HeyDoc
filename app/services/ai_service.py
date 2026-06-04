import hashlib
import json
import logging
import re

import httpx
from openai import AsyncOpenAI

from app.core.config import Settings
from app.repositories.cache_repository import cache_repository
from app.utils.helpers import try_parse_json


logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _get_client(self, api_key: str) -> AsyncOpenAI:
        return AsyncOpenAI(base_url=self.settings.openrouter_base_url, api_key=api_key)

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        import base64

        client = self._get_client(self.settings.openai_api_key or self.settings.openrouter_api_key)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        result = await client.chat.completions.create(
            model=self.settings.transcribe_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Transcribe this audio exactly."},
                        {"type": "input_audio", "input_audio": {"data": audio_b64, "format": "wav"}},
                    ],
                }
            ],
        )
        return (result.choices[0].message.content or "").strip()

    async def diarize_transcript(self, transcript: str) -> str:
        prompt = f"""You are a medical conversation analyst. Label each spoken line as DOCTOR or PATIENT.
Rules:
- DOCTOR: the clinician asking questions, examining, giving advice or instructions.
- PATIENT: the person describing symptoms, answering questions, expressing concerns.
- Alternate labels based on context, not just turn order.
- Output ONLY lines in this exact format (one per line, no extra text):
DOCTOR: <text>
PATIENT: <text>

Raw transcript:
{transcript}"""
        return await self._chat(prompt, max_tokens=2000)

    async def generate_soap(self, diarized_text: str) -> dict:
        prompt = f"""You are an expert medical scribe. Generate a SOAP note from this conversation.
Return ONLY valid JSON (no markdown):
{{"subjective":{{"chief_complaint":"...","history_of_present_illness":"...","symptoms":[],"duration":"...","severity":"..."}},"objective":{{"vitals":"...","physical_exam":"...","observations":[]}},"assessment":{{"diagnosis":"...","differential":[]}},"plan":{{"investigations":[],"medications":[],"follow_up":"...","instructions":"..."}}}}
Conversation:\n{diarized_text}"""
        response = await self._chat(prompt, max_tokens=1600)
        return try_parse_json(response)

    async def generate_patient_summary(self, soap: dict) -> str:
        prompt = f"""Write a short, warm, patient-friendly visit summary (under 150 words).
Use simple language and write in third person.
Start with "The patient came in today..."
Do NOT include any patient name or identifying information.
SOAP:\n{json.dumps(soap, indent=2)}"""
        return await self._chat(prompt, max_tokens=400)

    async def detect_transcript_issues(self, raw_text: str, diarized_text: str) -> list[dict]:
        prompt = f"""Review this medical transcript pair and find likely ASR/diarization inconsistencies.
Focus on:
- likely misheard medical terms or drug names
- wrong speaker assignment (DOCTOR vs PATIENT)
- contradictory wording that may change clinical meaning

Return ONLY valid JSON array with max 8 items:
[{{"issue":"...","suggestion":"...","severity":"high|medium|low"}}]

Raw transcript:
{raw_text}

Diarized transcript:
{diarized_text}
"""
        try:
            result = await self._chat(prompt, max_tokens=700)
            parsed = try_parse_json(result)
            return parsed if isinstance(parsed, list) else []
        except Exception:
            return []

    async def suggest_icd10(self, soap: dict) -> list[dict]:
        icd10_pattern = re.compile(r"^[A-Z]\d{2}(\.\d{0,4})?$")
        confidence_priority = {"high": 3, "medium": 2, "low": 1}
        fallback = [{"code": "-", "description": "Could not generate codes", "confidence": "low"}]
        excluded_codes = {"R69", "Z00.00", "Z00.01", "Z53.9", "R63.5"}

        async def _verify_code_exists(code: str) -> bool:
            try:
                url = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
                params = {"sf": "code", "terms": code, "maxList": 1}
                async with httpx.AsyncClient(timeout=3.0) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                data = response.json()
                codes_returned = data[1] if len(data) > 1 else []
                return code.upper() in [c.upper() for c in (codes_returned or [])]
            except Exception:
                return True

        def _is_valid_format(code: str) -> bool:
            return bool(icd10_pattern.match(code.strip().upper()))

        def _is_valid_entry(entry: dict) -> bool:
            if not isinstance(entry, dict):
                return False
            code = entry.get("code", "")
            description = entry.get("description", "")
            confidence = entry.get("confidence", "")
            return (
                isinstance(code, str)
                and _is_valid_format(code)
                and isinstance(description, str)
                and len(description.strip()) > 5
                and confidence in confidence_priority
            )

        async def _filter_and_verify(parsed: list) -> list[dict]:
            cleaned = []
            seen_prefixes = set()

            for entry in parsed:
                if not _is_valid_entry(entry):
                    continue

                code = entry["code"].strip().upper()
                confidence = entry["confidence"].lower()

                if code in excluded_codes:
                    logger.warning("icd10_excluded_code: %s", code)
                    continue

                if confidence == "low":
                    continue

                prefix = code[:3]
                if prefix in seen_prefixes:
                    logger.warning("icd10_duplicate_family: %s", code)
                    continue
                seen_prefixes.add(prefix)

                is_real = await _verify_code_exists(code)
                if not is_real:
                    logger.warning("icd10_code_not_found: %s", code)
                    continue

                cleaned.append(
                    {
                        "code": code,
                        "description": entry["description"].strip(),
                        "confidence": confidence,
                    }
                )

            cleaned.sort(key=lambda item: confidence_priority.get(item["confidence"], 0), reverse=True)
            return cleaned[:3]

        content_hash = hashlib.sha256(json.dumps(soap, sort_keys=True).encode("utf-8")).hexdigest()
        cache_key = f"icd10:{content_hash}"
        cached = cache_repository.get(cache_key)
        if cached is not None:
            return cached

        subjective = soap.get("subjective", {})
        assessment = soap.get("assessment", {})
        diagnosis = assessment.get("diagnosis") or "Not provided"
        differential = assessment.get("differential") or []
        chief_complaint = subjective.get("chief_complaint") or "Not provided"
        symptoms = subjective.get("symptoms") or []

        prompt = f"""You are a certified medical coder. Suggest exactly 3 ICD-10-CM codes based on the clinical data below.

STRICT RULES:
1. Return ONLY a valid JSON array - no prose, no markdown, no explanation.
2. Each object must have exactly these fields: "code", "description", "confidence".
3. "code" must be a real, valid ICD-10-CM code (e.g., "J18.9", "E11.65", "M54.5").
4. "description" must be the official ICD-10-CM description of that code.
5. "confidence" must be exactly one of: "high", "medium", or "low".
6. Never use vague codes like R69 unless absolutely nothing else applies.
7. Never suggest two codes from the same disease family (e.g. E11.x).
8. Codes must directly relate to the diagnosis, differential, or symptoms.
9. Do not repeat codes.

Output format (strict):
[{{"code":"X00.0","description":"Official description","confidence":"high"}}]

Clinical Data:
- Primary Diagnosis: {diagnosis}
- Differential Diagnoses: {", ".join(differential) if differential else "None"}
- Chief Complaint: {chief_complaint}
- Symptoms: {", ".join(symptoms) if symptoms else "None"}
"""

        for attempt in range(3):
            try:
                result = await self._chat(prompt, max_tokens=600)
                parsed = try_parse_json(result)

                if not isinstance(parsed, list) or len(parsed) == 0:
                    logger.warning("icd10_empty_response attempt=%s", attempt + 1)
                    continue

                verified = await _filter_and_verify(parsed)

                if not verified:
                    logger.warning("icd10_no_verified_codes attempt=%s", attempt + 1)
                    continue

                cache_repository.set(cache_key, verified, self.settings.cache_ttl_seconds)
                return verified

            except Exception as exc:
                logger.error("icd10_attempt_failed attempt=%s error=%s", attempt + 1, exc)

        return fallback

    async def generate_followup_reminder(self, soap: dict) -> str:
        plan = soap.get("plan", {})
        prompt = f"""Write a brief friendly SMS-style follow-up reminder (<120 words).
Start with "Hello," (no name). Include next steps, return date, who to call.
Do NOT include any patient name or identifying information.
Follow-up: {plan.get("follow_up")} Tests: {plan.get("investigations", [])} Meds: {plan.get("medications", [])}"""
        return await self._chat(prompt, max_tokens=220)

    async def _chat(self, prompt: str, max_tokens: int) -> str:
        client = self._get_client(self.settings.openrouter_api_key)
        response = await client.chat.completions.create(
            model=self.settings.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return (response.choices[0].message.content or "").strip()
