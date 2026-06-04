import asyncio
import base64
import datetime as dt
import json
import random
import re
import smtplib
from email.message import EmailMessage
from typing import Awaitable, Callable

import httpx

from app.core.config import Settings
from app.utils.helpers import from_base64


class DeliveryService:
    FAX_E164_REGEX = re.compile(r"^\+[1-9]\d{7,14}$")

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def send(self, channel: str, pdf_base64: str = "", **kwargs) -> dict:
        pdf_bytes = from_base64(pdf_base64) if pdf_base64 else b""
        retries = max(1, int(kwargs.get("retries") or self.settings.fax_retries))
        retry_delay = float(kwargs.get("retry_delay_seconds") or self.settings.fax_retry_delay_seconds)

        if channel == "mock":
            return await self.send_with_retry(
                self.send_via_mock,
                2,
                1.0,
                pdf_bytes=pdf_bytes,
                recipient=kwargs.get("recipient", "mock"),
            )

        if channel in {"kno2", "fax_kno2"}:
            return await self.send_with_retry(
                self.send_via_kno2,
                retries,
                retry_delay,
                pdf_bytes=pdf_bytes,
                fax_number=kwargs.get("fax_number", ""),
            )

        if channel == "fax_auto":
            return await self.send_fax_with_fallback(
                pdf_bytes,
                kwargs.get("fax_number", ""),
                kwargs.get("fallback_email", ""),
                kwargs.get("smtp_host", ""),
                int(kwargs.get("smtp_port", self.settings.smtp_port)),
                kwargs.get("sender_email", ""),
                kwargs.get("sender_password", ""),
            )

        if channel == "srfax":
            return await self.send_with_retry(
                self.send_via_srfax,
                retries,
                retry_delay,
                pdf_bytes=pdf_bytes,
                fax_number=kwargs.get("fax_number", ""),
            )

        if channel == "phaxio":
            return await self.send_with_retry(
                self.send_via_phaxio,
                retries,
                retry_delay,
                pdf_bytes=pdf_bytes,
                fax_number=kwargs.get("fax_number", ""),
            )

        if channel == "email":
            return await self.send_with_retry(
                self.send_via_email,
                2,
                1.0,
                pdf_bytes=pdf_bytes,
                to_email=kwargs.get("to_email", ""),
                smtp_host=kwargs.get("smtp_host", ""),
                smtp_port=int(kwargs.get("smtp_port", self.settings.smtp_port)),
                sender_email=kwargs.get("sender_email", ""),
                sender_password=kwargs.get("sender_password", ""),
                subject=kwargs.get("subject"),
                body=kwargs.get("body"),
                attach_pdf=bool(kwargs.get("attach_pdf", True)),
                attachment_name=kwargs.get("attachment_name"),
                provider_tag=kwargs.get("provider_tag", "email"),
            )

        return {
            "success": False,
            "provider": channel,
            "status": "failed",
            "message_id": None,
            "error": "Unsupported channel",
            "attempts": 0,
        }

    @staticmethod
    async def send_via_mock(pdf_bytes: bytes, recipient: str) -> dict:
        ok = random.random() > 0.2
        return {
            "success": ok,
            "message_id": f"MOCK-{random.randint(10000, 99999)}",
            "provider": "mock",
            "status": "sent" if ok else "failed",
            "error": None if ok else "Simulated failure",
            "recipient": recipient or "unknown",
        }

    @staticmethod
    def normalize_fax_number(value: str) -> str:
        raw = str(value or "").strip()
        if not raw:
            return ""
        if raw.startswith("+"):
            return "+" + re.sub(r"\D", "", raw[1:])
        return "+" + re.sub(r"\D", "", raw)

    @classmethod
    def is_valid_e164_fax(cls, fax_number: str) -> bool:
        return bool(cls.FAX_E164_REGEX.match(str(fax_number or "").strip()))

    @staticmethod
    def fax_region(fax_number: str) -> str:
        return "US" if str(fax_number or "").startswith("+1") else "INTL"

    async def send_with_retry(
        self,
        send_fn: Callable[..., Awaitable[dict]],
        retries: int,
        delay_seconds: float,
        **kwargs,
    ) -> dict:
        attempts = max(1, int(retries))
        last = {}
        for idx in range(1, attempts + 1):
            result = await send_fn(**kwargs)
            if result.get("success"):
                result["attempts"] = idx
                return result
            last = result
            if idx < attempts:
                await asyncio.sleep(max(0.0, float(delay_seconds)))
        last["attempts"] = attempts
        return last

    async def send_fax_with_fallback(
        self,
        pdf_bytes: bytes,
        fax_number: str,
        fallback_email: str = "",
        smtp_host: str = "",
        smtp_port: int = 465,
        sender_email: str = "",
        sender_password: str = "",
    ) -> dict:
        fax = self.normalize_fax_number(fax_number)
        if not self.is_valid_e164_fax(fax):
            return {
                "success": False,
                "message_id": None,
                "provider": "validation",
                "status": "failed",
                "error": "Invalid fax number. Use E.164 format, e.g. +12345678901",
                "attempts": 0,
                "route": [],
            }

        retries = max(1, self.settings.fax_retries)
        delay = max(0.0, self.settings.fax_retry_delay_seconds)
        region = self.fax_region(fax)
        route = ["kno2", "srfax", "phaxio"] if region == "US" else ["srfax", "phaxio", "kno2"]
        failures = []

        for provider in route:
            if provider == "kno2":
                result = await self.send_with_retry(
                    self.send_via_kno2,
                    retries,
                    delay,
                    pdf_bytes=pdf_bytes,
                    fax_number=fax,
                )
            elif provider == "srfax":
                result = await self.send_with_retry(
                    self.send_via_srfax,
                    retries,
                    delay,
                    pdf_bytes=pdf_bytes,
                    fax_number=fax,
                )
            else:
                result = await self.send_with_retry(
                    self.send_via_phaxio,
                    retries,
                    delay,
                    pdf_bytes=pdf_bytes,
                    fax_number=fax,
                )

            if result.get("success"):
                result["route"] = route
                result["fax_number"] = fax
                result["region"] = region
                return result

            failures.append(
                {
                    "provider": provider,
                    "error": result.get("error"),
                    "attempts": result.get("attempts"),
                }
            )

        smtp_host = smtp_host or self.settings.smtp_host
        smtp_port = int(smtp_port or self.settings.smtp_port)
        sender_email = sender_email or self.settings.sender_email
        sender_password = sender_password or self.settings.sender_password

        if fallback_email and sender_email and sender_password:
            email_result = await self.send_with_retry(
                self.send_via_email,
                2,
                1.0,
                pdf_bytes=pdf_bytes,
                to_email=fallback_email,
                smtp_host=smtp_host,
                smtp_port=smtp_port,
                sender_email=sender_email,
                sender_password=sender_password,
                subject=f"FAX delivery fallback - SOAP Note ({dt.date.today().isoformat()})",
                body=(
                    "Hello,\n\n"
                    "Fax delivery was unavailable, so this document was sent via secure email fallback.\n"
                    "Please handle per your organization's privacy policy."
                ),
                provider_tag="email_fallback",
            )
            if email_result.get("success"):
                email_result["route"] = route + ["email_fallback"]
                email_result["fax_number"] = fax
                email_result["region"] = region
                email_result["fallback_used"] = True
                return email_result

            failures.append(
                {
                    "provider": "email_fallback",
                    "error": email_result.get("error"),
                    "attempts": email_result.get("attempts"),
                }
            )

        return {
            "success": False,
            "message_id": None,
            "provider": "all_failed",
            "status": "failed",
            "error": "All fax providers failed.",
            "attempts": retries,
            "route": route,
            "fax_number": fax,
            "region": region,
            "failures": failures,
        }

    async def send_via_kno2(self, pdf_bytes: bytes, fax_number: str) -> dict:
        if not self.settings.base_url or not self.settings.api_key:
            return {
                "success": False,
                "message_id": None,
                "provider": "kno2",
                "status": "failed",
                "error": "Kno2 config missing",
            }

        try:
            headers = {"Authorization": f"Bearer {self.settings.api_key}", "Content-Type": "application/json"}
            timeout = self.settings.request_timeout_seconds
            async with httpx.AsyncClient(timeout=timeout) as client:
                created = await client.put(
                    f"{self.settings.base_url}/messages",
                    headers=headers,
                    json={
                        "to": [{"type": "Fax", "value": fax_number}],
                        "subject": "SOAP Note",
                        "body": "Medical document attached",
                    },
                )
                created.raise_for_status()
                message_id = created.json()["id"]

                attachments = await client.post(
                    f"{self.settings.base_url}/messages/{message_id}/attachments",
                    headers={"Authorization": f"Bearer {self.settings.api_key}"},
                    files={"file": ("soap.pdf", pdf_bytes, "application/pdf")},
                )
                attachments.raise_for_status()

                sent = await client.post(f"{self.settings.base_url}/messages/{message_id}/send", headers=headers)

            return {
                "success": sent.status_code == 200,
                "message_id": message_id,
                "provider": "kno2",
                "status": "sent" if sent.status_code == 200 else "failed",
                "error": None if sent.status_code == 200 else "Send failed",
            }
        except Exception as exc:
            return {
                "success": False,
                "message_id": None,
                "provider": "kno2",
                "status": "failed",
                "error": str(exc),
            }

    async def send_via_srfax(self, pdf_bytes: bytes, fax_number: str) -> dict:
        if not self.settings.srfax_access_id or not self.settings.srfax_access_pwd:
            return {
                "success": False,
                "message_id": None,
                "provider": "srfax",
                "status": "failed",
                "error": "SRFax config missing",
            }

        try:
            payload = {
                "action": "Queue_Fax",
                "access_id": self.settings.srfax_access_id,
                "access_pwd": self.settings.srfax_access_pwd,
                "sCallerID": "HeyDoc",
                "sToFaxNumber": fax_number,
                "sResponseFormat": "JSON",
                "sFileName_1": "soap.pdf",
                "sFileContent_1": base64.b64encode(pdf_bytes).decode("utf-8"),
                "sFileContentType_1": "PDF",
            }
            timeout = self.settings.request_timeout_seconds
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(self.settings.srfax_url, data=payload)
                response.raise_for_status()

            try:
                data = response.json()
            except Exception:
                data = json.loads(response.text)

            fax_id = str(data.get("Result") or data.get("faxid") or data.get("ID") or "")
            ok = str(data.get("Status", "")).lower() in {"success", "queued", "ok"} or bool(fax_id)
            return {
                "success": ok,
                "message_id": fax_id or f"SRFAX-{random.randint(10000, 99999)}",
                "provider": "srfax",
                "status": "queued" if ok else "failed",
                "error": None if ok else str(data),
            }
        except Exception as exc:
            return {
                "success": False,
                "message_id": None,
                "provider": "srfax",
                "status": "failed",
                "error": str(exc),
            }

    async def send_via_phaxio(self, pdf_bytes: bytes, fax_number: str) -> dict:
        if not self.settings.phaxio_api_key or not self.settings.phaxio_api_secret:
            return {
                "success": False,
                "message_id": None,
                "provider": "phaxio",
                "status": "failed",
                "error": "Phaxio config missing",
            }

        try:
            timeout = self.settings.request_timeout_seconds
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    "https://api.phaxio.com/v2/faxes",
                    auth=(self.settings.phaxio_api_key, self.settings.phaxio_api_secret),
                    data={"to": fax_number},
                    files={"file": ("soap.pdf", pdf_bytes, "application/pdf")},
                )
                response.raise_for_status()
                data = response.json()

            fax_id = str((data.get("data") or {}).get("id") or data.get("faxId") or "")
            ok = bool(data.get("success", True))
            return {
                "success": ok,
                "message_id": fax_id or f"PHAXIO-{random.randint(10000, 99999)}",
                "provider": "phaxio",
                "status": "queued" if ok else "failed",
                "error": None if ok else str(data),
            }
        except Exception as exc:
            return {
                "success": False,
                "message_id": None,
                "provider": "phaxio",
                "status": "failed",
                "error": str(exc),
            }

    async def send_via_email(
        self,
        pdf_bytes: bytes,
        to_email: str,
        smtp_host: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        subject: str | None = None,
        body: str | None = None,
        attach_pdf: bool = True,
        attachment_name: str | None = None,
        provider_tag: str = "email",
    ) -> dict:
        smtp_host = smtp_host or self.settings.smtp_host
        smtp_port = int(smtp_port or self.settings.smtp_port)
        requested_sender_email = sender_email.strip()
        smtp_sender_email = self.settings.sender_email or requested_sender_email
        smtp_sender_password = self.settings.sender_password or sender_password

        if not smtp_sender_email or not smtp_sender_password:
            return {
                "success": False,
                "message_id": None,
                "provider": provider_tag,
                "status": "failed",
                "error": "SMTP config missing. Configure SENDER_EMAIL and SENDER_PASSWORD on the server.",
            }

        try:
            msg = EmailMessage()
            msg["Subject"] = subject or f"SOAP Note - {dt.date.today().isoformat()}"
            msg["From"] = smtp_sender_email
            msg["To"] = to_email
            if requested_sender_email and requested_sender_email.lower() != smtp_sender_email.lower():
                msg["Reply-To"] = requested_sender_email
            msg.set_content(body or "SOAP note attached. Generated by HeyDoc AI Medical Scribe.")

            if attach_pdf and pdf_bytes:
                msg.add_attachment(
                    pdf_bytes,
                    maintype="application",
                    subtype="pdf",
                    filename=attachment_name or f"soap_{dt.date.today().isoformat()}.pdf",
                )

            def _send_message() -> None:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=self.settings.request_timeout_seconds) as smtp:
                    smtp.login(smtp_sender_email, smtp_sender_password)
                    smtp.send_message(msg)

            await asyncio.to_thread(_send_message)

            return {
                "success": True,
                "message_id": f"EMAIL-{random.randint(10000, 99999)}",
                "provider": provider_tag,
                "status": "sent",
                "error": None,
            }
        except Exception as exc:
            return {
                "success": False,
                "message_id": None,
                "provider": provider_tag,
                "status": "failed",
                "error": str(exc),
            }
