import base64
import csv
import datetime
import io
import json
import os
import random
import smtplib
import tempfile
import textwrap
import time
from email.message import EmailMessage
import requests
import openai
import requests
import streamlit as st

# ─── Config ───────────────────────────────────────────────────────────────────
MODEL = "openai/gpt-4o-mini"
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
BASE_URL = st.secrets["BASE_URL"]
API_KEY = st.secrets["API_KEY"]

SAMPLE_TRANSCRIPT = """Good morning, how are you feeling today?
I've been having chest pain for the past three days, it gets worse when I walk.
Can you describe the pain? Is it sharp or dull?
It's more like a pressure, kind of heavy feeling.
Any shortness of breath?
Yes, sometimes, especially when climbing stairs.
Do you have any fever or cough?
No fever, but I have a mild cough since yesterday.
Have you had any similar episodes before?
No, this is the first time.
Any family history of heart disease?
Yes, my father had a heart attack at 60.
Your blood pressure is 138 over 88 and heart rate is 94. I'm going to recommend an ECG and some blood tests.
What do you think it could be?
It could be angina or something related to the heart. We need to rule that out first.
Should I be worried?
Let's not jump to conclusions. Take this medication for now and we'll follow up after the tests. Come back in one week."""







headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def create_message(recipient_fax):
    payload = {
        "to": [
            {
                "type": "Fax",
                "value": recipient_fax
            }
        ],
        "subject": "SOAP Note",
        "body": "Medical document attached"
    }

    response = requests.post(
        f"{BASE_URL}/messages",
        headers=headers,
        json=payload
    )

    return response.json()

def attach_pdf(message_id, pdf_bytes):
    files = {
        "file": ("soap.pdf", pdf_bytes, "application/pdf")
    }

    response = requests.post(
        f"{BASE_URL}/messages/{message_id}/attachments",
        headers={"Authorization": f"Bearer {API_KEY}"},
        files=files
    )

    return response.status_code
def send_message(message_id):
    response = requests.post(
        f"{BASE_URL}/messages/{message_id}/send",
        headers=headers
    )

    return response.status_code




def send_via_kno2(pdf_bytes, fax_number):
    try:
        msg = create_message(fax_number)
        message_id = msg["id"]

        attach_pdf(message_id, pdf_bytes)

        send_status = send_message(message_id)

        return {
            "success": send_status == 200,
            "message_id": message_id,
            "provider": "kno2",
            "error": None if send_status == 200 else "Send failed"
        }

    except Exception as e:
        return {
            "success": False,
            "message_id": None,
            "provider": "kno2",
            "error": str(e)
        }
# ─── API helpers ──────────────────────────────────────────────────────────────
def get_client(api_key: str):
    return openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

_get_client = get_client


def transcribe_with_whisper(audio_path: str, api_key: str) -> str:
    client = get_client(api_key)
    with open(audio_path, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()
    response = client.chat.completions.create(
        model="google/gemini-3.1-flash-lite-preview",
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
    return response.choices[0].message.content


def diarize_transcript(transcript: str, api_key: str) -> str:
    client = get_client(api_key)
    prompt = f"""You are a medical conversation analyst.
Given the following raw transcript from a doctor-patient consultation,
identify and label each line as either DOCTOR or PATIENT based on:
- Doctors ask medical questions, give instructions, use clinical terms
- Patients describe symptoms, answer questions, express concerns

Return ONLY the diarized transcript in this exact format:
DOCTOR: <text>
PATIENT: <text>
(one line per speaker turn, no extra commentary)

Raw transcript:
{transcript}"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
    )
    return response.choices[0].message.content.strip()


def generate_soap(diarized: str, api_key: str) -> dict:
    client = get_client(api_key)
    prompt = f"""You are an expert medical scribe.
Based on the following doctor-patient conversation, generate a complete SOAP note.

Return ONLY valid JSON with this exact structure (no markdown, no backticks):
{{
  "subjective": {{
    "chief_complaint": "...",
    "history_of_present_illness": "...",
    "symptoms": ["symptom1", "symptom2"],
    "duration": "...",
    "severity": "..."
  }},
  "objective": {{
    "vitals": "...",
    "physical_exam": "...",
    "observations": ["obs1", "obs2"]
  }},
  "assessment": {{
    "diagnosis": "...",
    "differential": ["dx1", "dx2"]
  }},
  "plan": {{
    "investigations": ["test1", "test2"],
    "medications": ["med1", "med2"],
    "follow_up": "...",
    "instructions": "..."
  }}
}}

If any field is not mentioned in the conversation, write "Not documented" for strings or [] for arrays.

Conversation:
{diarized}"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def generate_patient_summary(soap: dict, api_key: str) -> str:
    client = get_client(api_key)
    prompt = f"""You are a compassionate medical communicator.
Based on the SOAP note below, write a short, warm, patient-friendly summary.

Rules:
- Use simple language (no medical jargon)
- Be empathetic and reassuring
- Include: what was discussed, what was recommended, and next steps
- Keep it under 150 words
- Write in 2nd person ("You came in today...")

SOAP Note:
{json.dumps(soap, indent=2)}"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
    )
    return response.choices[0].message.content.strip()


def format_soap_markdown(soap: dict) -> str:
    s = soap.get("subjective", {})
    o = soap.get("objective", {})
    a = soap.get("assessment", {})
    p = soap.get("plan", {})

    def value(text):
        if text in (None, "", []):
            return "Not documented"
        return str(text).strip()

    def bullets(items):
        if not items:
            return "- Not documented"
        cleaned = [str(item).strip() for item in items if str(item).strip()]
        return "\n".join(f"- {item}" for item in cleaned) if cleaned else "- Not documented"

    return f"""# SOAP Note

> ⚠️ *AI-generated clinical documentation draft. Review and verify before sharing or adding to the medical record.*

## 📋 S — Subjective
**Chief Complaint:** {value(s.get('chief_complaint'))}

**History of Present Illness:** {value(s.get('history_of_present_illness'))}

**Duration:** {value(s.get('duration'))}

**Severity:** {value(s.get('severity'))}

**Reported Symptoms:**
{bullets(s.get('symptoms', []))}

---

## 🩺 O — Objective
**Vitals:** {value(o.get('vitals'))}

**Physical Examination:** {value(o.get('physical_exam'))}

**Clinical Observations:**
{bullets(o.get('observations', []))}

---

## 🔍 A — Assessment
**Primary Impression:** {value(a.get('diagnosis'))}

**Differential Diagnoses:**
{bullets(a.get('differential', []))}

---

## 📌 P — Plan
**Investigations / Orders:**
{bullets(p.get('investigations', []))}

**Medications / Treatments:**
{bullets(p.get('medications', []))}

**Follow-Up:** {value(p.get('follow_up'))}

**Patient Instructions:** {value(p.get('instructions'))}
"""


def create_soap_pdf_bytes(soap: dict) -> bytes:
    import io
    import datetime
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )

    s = soap.get("subjective", {})
    o = soap.get("objective", {})
    a = soap.get("assessment", {})
    p = soap.get("plan", {})

    def val(text):
        if text in (None, "", []):
            return "Not documented"
        return str(text).strip()

    def bullet_list(items):
        if not items:
            return [("• Not documented", False)]
        return [(f"• {str(i).strip()}", False) for i in items if str(i).strip()]

    # ── Colour palette ──────────────────────────────────────────────────────
    NAVY        = colors.HexColor("#003A75")
    TEAL        = colors.HexColor("#00897B")
    BLUE_LIGHT  = colors.HexColor("#0066CC")
    SECTION_BG  = colors.HexColor("#EBF3FB")
    WARN_BG     = colors.HexColor("#FFF8E1")
    WARN_BORDER = colors.HexColor("#F59E0B")
    TEXT_DARK   = colors.HexColor("#1A202C")
    TEXT_MID    = colors.HexColor("#4A5568")
    RULE_COLOR  = colors.HexColor("#CBD5E0")
    WHITE       = colors.white

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.75 * inch,
        title="SOAP Note — HeyDoc AI Medical Scribe",
    )

    # ── Styles ───────────────────────────────────────────────────────────────
    base = getSampleStyleSheet()

    def ps(name, parent="Normal", **kw):
        return ParagraphStyle(name, parent=base[parent], **kw)

    st_doc_title = ps("DocTitle",
        fontSize=22, leading=26, textColor=WHITE,
        fontName="Helvetica-Bold", alignment=TA_CENTER)

    st_doc_sub = ps("DocSub",
        fontSize=9, leading=13, textColor=colors.HexColor("#B0C4DE"),
        fontName="Helvetica", alignment=TA_CENTER)

    st_section = ps("Section",
        fontSize=11, leading=14, textColor=WHITE,
        fontName="Helvetica-Bold", spaceAfter=0)

    st_label = ps("Label",
        fontSize=8.5, leading=11, textColor=BLUE_LIGHT,
        fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=1)

    st_body = ps("Body",
        fontSize=9.5, leading=14, textColor=TEXT_DARK,
        fontName="Helvetica", spaceAfter=4)

    st_bullet = ps("Bullet",
        fontSize=9.5, leading=14, textColor=TEXT_DARK,
        fontName="Helvetica", leftIndent=10, spaceAfter=2)

    st_warn = ps("Warn",
        fontSize=8, leading=12, textColor=colors.HexColor("#7A4F01"),
        fontName="Helvetica-Oblique")

    st_footer = ps("Footer",
        fontSize=7.5, leading=10, textColor=TEXT_MID,
        fontName="Helvetica", alignment=TA_CENTER)

    # ── Helper builders ──────────────────────────────────────────────────────
    def section_header(letter_badge, title, accent=NAVY):
        """Coloured section header row with letter badge."""
        badge = Paragraph(f"<b>{letter_badge}</b>",
                          ParagraphStyle("badge", fontSize=13, textColor=WHITE,
                                         fontName="Helvetica-Bold", alignment=TA_CENTER))
        heading = Paragraph(title, st_section)
        tbl = Table([[badge, heading]], colWidths=[0.38 * inch, None])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, -1), accent),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [accent]),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING",  (0, 0), (0, 0), 6),
            ("RIGHTPADDING", (0, 0), (0, 0), 4),
            ("LEFTPADDING",  (1, 0), (1, 0), 8),
            ("TOPPADDING",   (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
            ("ROUNDEDCORNERS", [4]),
        ]))
        return tbl

    def field_row(label, value, full_width=True):
        """Two-column label / value pair inside a light card."""
        lbl = Paragraph(label.upper(), st_label)
        val_p = Paragraph(val(value), st_body)
        if full_width:
            tbl = Table([[lbl], [val_p]], colWidths=[None])
        else:
            tbl = Table([[lbl, val_p]], colWidths=[1.4 * inch, None])
        return tbl

    def card(*elements, bg=SECTION_BG):
        """Wrap elements in a shaded card table."""
        inner = [[e] for e in elements]
        tbl = Table(inner, colWidths=[doc.width])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), bg),
            ("TOPPADDING",   (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
            ("LEFTPADDING",  (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("ROUNDEDCORNERS", [4]),
        ]))
        return tbl

    def bullets_card(items_raw):
        paras = []
        for txt, _ in bullet_list(items_raw):
            paras.append(Paragraph(txt, st_bullet))
        return card(*paras)

    def hr():
        return HRFlowable(width="100%", thickness=0.5, color=RULE_COLOR,
                          spaceAfter=8, spaceBefore=4)

    # ── Build story ──────────────────────────────────────────────────────────
    story = []

    # ── Cover header ─────────────────────────────────────────────────────────
    today = datetime.date.today().strftime("%B %d, %Y")
    header_data = [
        [Paragraph("SOAP NOTE", st_doc_title)],
        [Paragraph("HeyDoc · AI-Powered Medical Scribe", st_doc_sub)],
        [Paragraph(f"Generated: {today}", st_doc_sub)],
    ]
    header_tbl = Table(header_data, colWidths=[doc.width])
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LEFTPADDING",  (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 10))

    # Disclaimer banner
    warn_tbl = Table(
        [[Paragraph("⚠  AI-generated draft — review and verify before adding to the medical record or sharing with third parties.", st_warn)]],
        colWidths=[doc.width]
    )
    warn_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), WARN_BG),
        ("LINEAFTER",    (0, 0), (0, -1), 3, WARN_BORDER),  # left border trick
        ("LINEBEFORE",   (0, 0), (0, -1), 3, WARN_BORDER),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(warn_tbl)
    story.append(Spacer(1, 14))

    # ── S — SUBJECTIVE ───────────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("S", "SUBJECTIVE", NAVY),
        Spacer(1, 6),
        card(
            Paragraph("CHIEF COMPLAINT", st_label),
            Paragraph(val(s.get("chief_complaint")), st_body),
            Paragraph("HISTORY OF PRESENT ILLNESS", st_label),
            Paragraph(val(s.get("history_of_present_illness")), st_body),
        ),
        Spacer(1, 6),
    ]))

    # Duration + Severity side by side
    two_col = Table([
        [
            card(
                Paragraph("DURATION", st_label),
                Paragraph(val(s.get("duration")), st_body),
            ),
            card(
                Paragraph("SEVERITY", st_label),
                Paragraph(val(s.get("severity")), st_body),
            ),
        ]
    ], colWidths=[doc.width / 2 - 4, doc.width / 2 - 4], hAlign="LEFT")
    two_col.setStyle(TableStyle([("LEFTPADDING", (0,0), (-1,-1), 0),
                                  ("RIGHTPADDING", (0,0), (-1,-1), 0),
                                  ("TOPPADDING", (0,0), (-1,-1), 0),
                                  ("BOTTOMPADDING", (0,0), (-1,-1), 0),
                                  ("INNERGRID", (0,0), (-1,-1), 0, colors.white),]))
    story.append(two_col)
    story.append(Spacer(1, 6))

    story.append(Paragraph("REPORTED SYMPTOMS", st_label))
    story.append(bullets_card(s.get("symptoms", [])))
    story.append(Spacer(1, 14))
    story.append(hr())

    # ── O — OBJECTIVE ────────────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("O", "OBJECTIVE", colors.HexColor("#005A8E")),
        Spacer(1, 6),
        card(
            Paragraph("VITALS", st_label),
            Paragraph(val(o.get("vitals")), st_body),
            Paragraph("PHYSICAL EXAMINATION", st_label),
            Paragraph(val(o.get("physical_exam")), st_body),
        ),
        Spacer(1, 6),
    ]))

    story.append(Paragraph("CLINICAL OBSERVATIONS", st_label))
    story.append(bullets_card(o.get("observations", [])))
    story.append(Spacer(1, 14))
    story.append(hr())

    # ── A — ASSESSMENT ───────────────────────────────────────────────────────
    story.append(KeepTogether([
        section_header("A", "ASSESSMENT", TEAL),
        Spacer(1, 6),
        card(
            Paragraph("PRIMARY IMPRESSION", st_label),
            Paragraph(val(a.get("diagnosis")), st_body),
        ),
        Spacer(1, 6),
    ]))

    story.append(Paragraph("DIFFERENTIAL DIAGNOSES", st_label))
    story.append(bullets_card(a.get("differential", [])))
    story.append(Spacer(1, 14))
    story.append(hr())

    # ── P — PLAN ─────────────────────────────────────────────────────────────
    story.append(section_header("P", "PLAN", colors.HexColor("#1A5276")))
    story.append(Spacer(1, 6))

    story.append(Paragraph("INVESTIGATIONS / ORDERS", st_label))
    story.append(bullets_card(p.get("investigations", [])))
    story.append(Spacer(1, 6))

    story.append(Paragraph("MEDICATIONS / TREATMENTS", st_label))
    story.append(bullets_card(p.get("medications", [])))
    story.append(Spacer(1, 6))

    story.append(card(
        Paragraph("FOLLOW-UP", st_label),
        Paragraph(val(p.get("follow_up")), st_body),
        Paragraph("PATIENT INSTRUCTIONS", st_label),
        Paragraph(val(p.get("instructions")), st_body),
    ))
    story.append(Spacer(1, 20))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(hr())
    story.append(Paragraph(
        f"HeyDoc AI Medical Scribe  ·  {today}  ·  All AI-generated notes must be reviewed by a licensed clinician before clinical use.",
        st_footer
    ))

    doc.build(story)
    return buf.getvalue()


def run_pipeline(audio_file, transcript_text):
    if not OPENROUTER_API_KEY.strip():
        raise ValueError("Set OPENROUTER_API_KEY before running the app.")

    transcript = ""
    temp_audio_path = None

    if audio_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.getbuffer())
            temp_audio_path = tmp.name
        transcript = transcribe_with_whisper(temp_audio_path, OPENAI_API_KEY)
    elif transcript_text.strip():
        transcript = transcript_text.strip()
    else:
        raise ValueError("Provide an audio file or paste a transcript.")

    diarized = diarize_transcript(transcript, OPENROUTER_API_KEY)
    soap = generate_soap(diarized, OPENROUTER_API_KEY)
    soap_markdown = format_soap_markdown(soap)
    patient_summary = generate_patient_summary(soap, OPENROUTER_API_KEY)
    soap_pdf = create_soap_pdf_bytes(soap)

    if temp_audio_path:
        try:
            os.unlink(temp_audio_path)
        except OSError:
            pass

    return transcript, diarized, soap_markdown, patient_summary, soap_pdf, soap


# ══════════════════════════════════════════════════════════════════════════════
# ADDON — FAX / EMAIL TRANSMISSION HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def send_via_mock(pdf_bytes: bytes, recipient: dict) -> dict:
    time.sleep(0.8)
    success = random.random() > 0.2
    return {
        "success": success,
        "message_id": f"MOCK-{random.randint(10000, 99999)}",
        "provider": "mock",
        "timestamp": datetime.datetime.now().isoformat(),
        "recipient": recipient,
        "error": None if success else "Simulated transmission failure",
    }


def send_via_webhook_site(pdf_bytes: bytes, recipient: dict, webhook_url: str) -> dict:
    encoded = base64.b64encode(pdf_bytes).decode("utf-8")
    payload = {
        "recipient": recipient,
        "document": {
            "filename": "soap_note.pdf",
            "content_type": "application/pdf",
            "data_base64": encoded[:100] + "...[truncated for display]",
            "size_bytes": len(pdf_bytes),
        },
        "sent_at": datetime.datetime.now().isoformat(),
    }
    try:
        r = requests.post(webhook_url, json=payload, timeout=10)
        return {
            "success": r.status_code < 400,
            "message_id": f"WH-{random.randint(10000,99999)}",
            "provider": "webhook.site",
            "timestamp": datetime.datetime.now().isoformat(),
            "recipient": recipient,
            "error": None if r.status_code < 400 else r.text,
        }
    except Exception as e:
        return {"success": False, "message_id": None, "provider": "webhook.site",
                "timestamp": datetime.datetime.now().isoformat(), "recipient": recipient, "error": str(e)}


def send_via_email(pdf_bytes: bytes, to_email: str,
                   smtp_host: str, smtp_port: int,
                   sender_email: str, sender_password: str,
                   patient_name: str = "Patient") -> dict:
    try:
        msg = EmailMessage()
        msg["Subject"] = f"SOAP Note — {patient_name} — {datetime.date.today()}"
        msg["From"] = sender_email
        msg["To"] = to_email
        msg.set_content(
            f"Please find the attached SOAP note for {patient_name}.\n\n"
            "This document was generated by HeyDoc AI Medical Scribe.\n"
            "Review and verify before clinical use."
        )
        msg.add_attachment(
            pdf_bytes,
            maintype="application",
            subtype="pdf",
            filename=f"soap_{patient_name.replace(' ', '_')}_{datetime.date.today()}.pdf",
        )
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return {
            "success": True,
            "message_id": f"EMAIL-{random.randint(10000,99999)}",
            "provider": "email",
            "timestamp": datetime.datetime.now().isoformat(),
            "recipient": {"email": to_email},
            "error": None,
        }
    except Exception as e:
        return {"success": False, "message_id": None, "provider": "email",
                "timestamp": datetime.datetime.now().isoformat(),
                "recipient": {"email": to_email}, "error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# ADDON — RETRY + FALLBACK
# ══════════════════════════════════════════════════════════════════════════════

def send_with_retry(send_fn, retries: int = 3, delay: float = 2.0, **kwargs) -> dict:
    last_result = {}
    for attempt in range(1, retries + 1):
        result = send_fn(**kwargs)
        if result["success"]:
            result["attempts"] = attempt
            return result
        last_result = result
        if attempt < retries:
            time.sleep(delay)
    last_result["attempts"] = retries
    return last_result


def send_with_fallback(pdf_bytes: bytes, recipient: dict,
                        primary_fn, fallback_fn,
                        primary_kwargs: dict, fallback_kwargs: dict) -> dict:
    result = send_with_retry(primary_fn, retries=2, **primary_kwargs)
    if result["success"]:
        result["used_fallback"] = False
        return result
    result = send_with_retry(fallback_fn, retries=2, **fallback_kwargs)
    result["used_fallback"] = True
    result["primary_error"] = primary_kwargs.get("error", "Primary failed")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# ADDON — AUDIT LOG
# ══════════════════════════════════════════════════════════════════════════════

def init_audit_log():
    if "audit_log" not in st.session_state:
        st.session_state.audit_log = []


def log_event(action: str, patient_name: str, details: dict):
    init_audit_log()
    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "patient": patient_name,
        **details,
    }
    st.session_state.audit_log.append(entry)


def export_audit_log_csv() -> bytes:
    if not st.session_state.get("audit_log"):
        return b""

    buf = io.StringIO()
    log = st.session_state.audit_log

    # 🔥 Collect ALL keys from all entries
    all_keys = set()
    for entry in log:
        all_keys.update(entry.keys())

    fieldnames = list(all_keys)

    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()

    for entry in log:
        writer.writerow(entry)

    return buf.getvalue().encode("utf-8")


def render_audit_log_ui():
    init_audit_log()
    log = st.session_state.audit_log
    if not log:
        st.info("No events logged yet.")
        return

    color_map = {
        "GENERATED": "#0066CC",
        "SENT":      "#00897B",
        "FAILED":    "#D32F2F",
        "DOWNLOADED":"#7C3AED",
        "VIEWED":    "#475569",
    }

    rows_html = ""
    for entry in reversed(log[-20:]):
        color = color_map.get(entry.get("action", ""), "#475569")
        rows_html += f"""
        <tr>
          <td style="color:#94A3B8;font-size:.78rem;">{entry.get('timestamp','')}</td>
          <td><span style="background:{color}22;color:{color};padding:2px 8px;
              border-radius:20px;font-size:.75rem;font-weight:600;">
              {entry.get('action','')}</span></td>
          <td style="color:#CBD5E1;font-size:.82rem;">{entry.get('patient','—')}</td>
          <td style="color:#64748B;font-size:.78rem;">{entry.get('provider','—')}</td>
          <td style="color:#64748B;font-size:.78rem;">{entry.get('message_id','—')}</td>
        </tr>"""

    st.markdown(f"""
    <table style="width:100%;border-collapse:collapse;">
      <thead>
        <tr style="border-bottom:1px solid #1E3A5F;">
          <th style="color:#475569;font-size:.72rem;text-align:left;padding:6px 4px;">TIME</th>
          <th style="color:#475569;font-size:.72rem;text-align:left;padding:6px 4px;">ACTION</th>
          <th style="color:#475569;font-size:.72rem;text-align:left;padding:6px 4px;">PATIENT</th>
          <th style="color:#475569;font-size:.72rem;text-align:left;padding:6px 4px;">PROVIDER</th>
          <th style="color:#475569;font-size:.72rem;text-align:left;padding:6px 4px;">MESSAGE ID</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

    csv_bytes = export_audit_log_csv()
    if csv_bytes:
        st.download_button(
            "⬇️ Export Audit Log CSV",
            data=csv_bytes,
            file_name=f"heydoc_audit_{datetime.date.today()}.csv",
            mime="text/csv",
        )


# ══════════════════════════════════════════════════════════════════════════════
# ADDON — ICD-10 CODE SUGGESTER
# ══════════════════════════════════════════════════════════════════════════════

def suggest_icd10_codes(soap: dict, api_key: str) -> list:
    client = _get_client(api_key)
    assessment = soap.get("assessment", {})
    subjective = soap.get("subjective", {})

    prompt = f"""You are a medical coding specialist.
Based on the diagnosis and symptoms below, suggest the 3 most relevant ICD-10 codes.

Primary diagnosis: {assessment.get('diagnosis', 'Not documented')}
Differential diagnoses: {assessment.get('differential', [])}
Chief complaint: {subjective.get('chief_complaint', 'Not documented')}
Symptoms: {subjective.get('symptoms', [])}

Return ONLY valid JSON array, no markdown:
[
  {{"code": "X00.0", "description": "Full ICD-10 description", "confidence": "high|medium|low"}},
  ...
]"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception:
        return [{"code": "—", "description": "Could not generate codes", "confidence": "low"}]


def render_icd10_ui(soap: dict, api_key: str):
    st.markdown('<div class="section-label">🏷️ ICD-10 Code Suggestions</div>', unsafe_allow_html=True)
    if st.button("🔍 Suggest ICD-10 Codes", key="icd10_btn"):
        with st.spinner("Analysing assessment for ICD-10 codes..."):
            codes = suggest_icd10_codes(soap, api_key)
            st.session_state["icd10_codes"] = codes
            log_event("VIEWED", "unknown", {"action_detail": "ICD-10 codes generated", "provider": "—", "message_id": "—"})

    if "icd10_codes" in st.session_state:
        confidence_color = {"high": "#00897B", "medium": "#F59E0B", "low": "#D32F2F"}
        for item in st.session_state["icd10_codes"]:
            color = confidence_color.get(item.get("confidence", "low"), "#475569")
            st.markdown(f"""
            <div style="background:#0F172A;border:1px solid #1E3A5F;border-radius:8px;
                        padding:10px 14px;margin-bottom:8px;display:flex;
                        align-items:center;gap:14px;">
              <span style="font-family:monospace;font-weight:700;color:#60A5FA;
                           font-size:1rem;min-width:70px;">{item.get('code','—')}</span>
              <span style="color:#CBD5E1;font-size:.85rem;flex:1;">{item.get('description','—')}</span>
              <span style="background:{color}22;color:{color};padding:2px 8px;
                           border-radius:20px;font-size:.72rem;font-weight:600;">
                           {item.get('confidence','—')}</span>
            </div>""", unsafe_allow_html=True)
        st.caption("⚠️ AI suggestions only — verify with a certified medical coder before billing.")


# ══════════════════════════════════════════════════════════════════════════════
# ADDON — FOLLOW-UP REMINDER GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def generate_followup_reminder(soap: dict, api_key: str, patient_name: str = "Patient") -> str:
    client = _get_client(api_key)
    plan = soap.get("plan", {})

    prompt = f"""You are a clinic coordinator.
Write a brief, friendly follow-up reminder message for a patient based on their visit plan.

Patient name: {patient_name}
Follow-up instruction: {plan.get('follow_up', 'Not specified')}
Investigations ordered: {plan.get('investigations', [])}
Medications: {plan.get('medications', [])}
Instructions: {plan.get('instructions', 'Not specified')}

Write a short SMS-style reminder (under 120 words). Be warm and clear.
Start with "Hi {patient_name},"
Include: what to do next, when to come back, who to call if concerned."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate reminder: {e}"


def render_followup_ui(soap: dict, api_key: str):
    st.markdown('<div class="section-label">🔔 Follow-Up Reminder</div>', unsafe_allow_html=True)
    patient_name = st.text_input("Patient name for reminder", value="Patient", key="fu_name")
    if st.button("📲 Generate Follow-Up Reminder", key="fu_btn"):
        with st.spinner("Generating reminder..."):
            reminder = generate_followup_reminder(soap, api_key, patient_name)
            st.session_state["followup_reminder"] = reminder

    if "followup_reminder" in st.session_state:
        st.text_area(
            "Reminder message (editable before sending)",
            value=st.session_state["followup_reminder"],
            height=130,
            key="fu_text",
        )
        st.caption("📋 Copy this to your SMS system, patient portal, or email client.")


# ══════════════════════════════════════════════════════════════════════════════
# ADDON — MULTI-PATIENT SESSION MANAGER
# ══════════════════════════════════════════════════════════════════════════════

def init_patient_sessions():
    if "patient_sessions" not in st.session_state:
        st.session_state.patient_sessions = []


def save_current_to_session(patient_name: str, soap: dict,
                             soap_pdf_bytes: bytes, patient_summary: str):
    init_patient_sessions()
    entry = {
        "id": len(st.session_state.patient_sessions) + 1,
        "name": patient_name or f"Patient {len(st.session_state.patient_sessions) + 1}",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "soap": soap,
        "pdf_bytes": soap_pdf_bytes,
        "summary": patient_summary,
        "diagnosis": soap.get("assessment", {}).get("diagnosis", "Unknown"),
    }
    st.session_state.patient_sessions.append(entry)
    log_event("GENERATED", entry["name"], {"diagnosis": entry["diagnosis"], "provider": "—", "message_id": "—"})
    return entry["id"]


def render_session_manager_ui():
    init_patient_sessions()
    sessions = st.session_state.patient_sessions
    st.markdown('<div class="section-label">👥 Today\'s Patient Sessions</div>', unsafe_allow_html=True)
    if not sessions:
        st.info("No patients saved yet. Run the pipeline and save a session.")
        return
    for s in reversed(sessions):
        with st.expander(f"🧑‍⚕️ {s['name']}  ·  {s['timestamp']}  ·  {s['diagnosis']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Diagnosis:** {s['diagnosis']}")
                st.markdown(f"**Summary:**\n{s['summary']}")
            with col2:
                if s["pdf_bytes"]:
                    st.download_button(
                        "⬇️ Download PDF",
                        data=s["pdf_bytes"],
                        file_name=f"soap_{s['name'].replace(' ','_')}_{s['id']}.pdf",
                        mime="application/pdf",
                        key=f"dl_{s['id']}",
                    )


# ══════════════════════════════════════════════════════════════════════════════
# ADDON — TRANSMISSION UI
# ══════════════════════════════════════════════════════════════════════════════

def render_transmission_ui(soap_pdf_bytes: bytes, patient_name: str = ""):
    st.markdown('<div class="section-label">📡 Send Document</div>', unsafe_allow_html=True)
    if not soap_pdf_bytes:
        st.info("Generate a SOAP note first, then send it here.")
        return

    with st.form("transmission_form"):
        st.markdown("**Recipient Details**")
        col1, col2 = st.columns(2)
        with col1:
            recipient_name = st.text_input("Recipient name", placeholder="Dr. Smith / City Hospital")
            recipient_type = st.selectbox("Recipient type", ["Hospital/Specialist", "Lab", "Medicare/Insurance", "Another Clinic", "Patient (summary)"])
        with col2:
            fax_number = st.text_input("Fax number", placeholder="+1XXXXXXXXXX")
            email_addr = st.text_input("Email (optional)", placeholder="doctor@hospital.com")

        st.markdown("**Transmission Method**")
        method = st.radio(
            "Send via",
            ["Mock (test — no real send)", "Webhook.site (inspect payload)", "Kno2 Fax", "Email"],
            horizontal=True,
        )
        webhook_url = ""
        if method == "Webhook.site (inspect payload)":
            webhook_url = st.text_input("Your webhook.site URL", placeholder="https://webhook.site/...")

        smtp_host = smtp_port = sender_email = sender_password = ""
        if method == "Email":
            smtp_host       = st.text_input("SMTP host", value="smtp.gmail.com")
            smtp_port       = st.number_input("SMTP port", value=465)
            sender_email    = st.text_input("Sender email")
            sender_password = st.text_input("App password", type="password")

        submitted = st.form_submit_button("📤 Send Document", type="primary", use_container_width=True)

    if submitted:
        recipient = {"name": recipient_name, "type": recipient_type, "fax": fax_number, "email": email_addr}
        with st.spinner("Sending..."):
            if method == "Mock (test — no real send)":
                result = send_with_retry(send_via_mock, retries=3, pdf_bytes=soap_pdf_bytes, recipient=recipient)
            elif method == "Webhook.site (inspect payload)" and webhook_url:
                result = send_with_retry(send_via_webhook_site, retries=2,
                                         pdf_bytes=soap_pdf_bytes, recipient=recipient, webhook_url=webhook_url)
            elif method == "Kno2 Fax":
                result = send_via_kno2(soap_pdf_bytes, fax_number)
            elif method == "Email" and sender_email:
                result = send_with_retry(
                    send_via_email, retries=2,
                    pdf_bytes=soap_pdf_bytes, to_email=email_addr or sender_email,
                    smtp_host=smtp_host, smtp_port=int(smtp_port),
                    sender_email=sender_email, sender_password=sender_password,
                    patient_name=patient_name,
                )
            else:
                st.warning("Please fill in all required fields for the selected method.")
                return

        action = "SENT" if result["success"] else "FAILED"
        log_event(action, patient_name, {
            "provider": result.get("provider"),
            "message_id": result.get("message_id"),
            "recipient": recipient_name,
            "attempts": result.get("attempts", 1),
        })

        if result["success"]:
            st.success(f"✅ Sent via {result['provider'].upper()}  ·  ID: `{result['message_id']}`  ·  Attempts: {result.get('attempts', 1)}")
        else:
            st.error(f"❌ Failed after {result.get('attempts', 1)} attempts  ·  Error: {result.get('error', 'Unknown')}")
            if result.get("used_fallback"):
                st.warning("⚠️ Fallback provider also failed. Check credentials and retry.")


# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HeyDoc · AI Medical Scribe",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS (unchanged from original) ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif !important; }
.stApp { background: #0A0F1E !important; }
.heydoc-header {
    background: linear-gradient(135deg, #003A75 0%, #0066CC 55%, #00897B 100%);
    padding: 28px 36px; border-radius: 14px; margin-bottom: 28px;
    display: flex; align-items: center; gap: 20px;
    box-shadow: 0 8px 32px rgba(0, 102, 204, 0.25);
}
.heydoc-header h1 { font-size: 2rem; font-weight: 700; color: white; margin: 0; letter-spacing: -0.03em; }
.heydoc-header p { color: rgba(255,255,255,0.82); margin: 5px 0 0; font-size: 0.88rem; line-height: 1.5; }
.steps-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 24px; }
.step-badge {
    background: rgba(0, 102, 204, 0.15); color: #60A5FA;
    border: 1px solid rgba(0, 102, 204, 0.3); border-radius: 20px;
    padding: 5px 14px; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.01em;
}
.section-card { background: #0F172A; border: 1px solid #1E3A5F; border-radius: 12px; padding: 22px 24px; margin-bottom: 18px; }
.section-label { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #60A5FA; margin-bottom: 12px; }
.stTextArea textarea {
    background: #111827 !important; color: #E2E8F0 !important; border: 1px solid #1E3A5F !important;
    border-radius: 8px !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 0.82rem !important;
}
.stTextArea textarea:focus { border-color: #0066CC !important; box-shadow: 0 0 0 3px rgba(0,102,204,0.15) !important; }
label, .stTextArea label, .stFileUploader label { color: #94A3B8 !important; font-size: 0.82rem !important; font-weight: 500 !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0066CC, #0052A3) !important; color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important; font-size: 0.9rem !important;
    padding: 10px 28px !important; letter-spacing: 0.01em !important; transition: all 0.2s !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #0052A3, #003D7A) !important;
    box-shadow: 0 4px 18px rgba(0,102,204,0.35) !important; transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important; color: #60A5FA !important;
    border: 1.5px solid #1E3A5F !important; border-radius: 8px !important; font-weight: 600 !important;
}
.stButton > button[kind="secondary"]:hover { border-color: #60A5FA !important; background: rgba(96, 165, 250, 0.05) !important; }
.stTabs [data-baseweb="tab-list"] { background: #0F172A !important; border-bottom: 1px solid #1E3A5F !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] { color: #64748B !important; font-weight: 600 !important; font-size: 0.84rem !important; border-radius: 8px 8px 0 0 !important; padding: 10px 18px !important; }
.stTabs [aria-selected="true"] { color: #60A5FA !important; background: rgba(0,102,204,0.1) !important; border-bottom: 2px solid #0066CC !important; }
.stTabs [data-baseweb="tab-panel"] { background: #0F172A !important; border: 1px solid #1E3A5F !important; border-top: none !important; border-radius: 0 0 10px 10px !important; padding: 20px !important; }
.stMarkdown h1 { color: #E2E8F0 !important; font-size: 1.3rem !important; }
.stMarkdown h2 { color: #93C5FD !important; font-size: 1.05rem !important; margin-top: 1.2em !important; }
.stMarkdown p, .stMarkdown li { color: #CBD5E1 !important; line-height: 1.7 !important; }
.stMarkdown strong { color: #E2E8F0 !important; }
.stMarkdown hr { border-color: #1E3A5F !important; }
.stMarkdown blockquote { border-left: 3px solid #F59E0B !important; background: rgba(245,158,11,0.07) !important; padding: 8px 14px !important; border-radius: 0 6px 6px 0 !important; color: #FCD34D !important; }
.stFileUploader > div { background: #111827 !important; border: 1px dashed #1E3A5F !important; border-radius: 10px !important; }
.stFileUploader > div:hover { border-color: #0066CC !important; }
.stDownloadButton > button { background: linear-gradient(135deg, #00897B, #006B60) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; font-size: 0.85rem !important; width: 100% !important; }
.stSuccess { background: rgba(0, 137, 123, 0.12) !important; border: 1px solid #00897B !important; border-radius: 8px !important; color: #4DD0C4 !important; }
.stError { background: rgba(211, 47, 47, 0.1) !important; border: 1px solid #D32F2F !important; border-radius: 8px !important; }
.stInfo { background: rgba(0, 102, 204, 0.1) !important; border: 1px solid #0066CC !important; border-radius: 8px !important; color: #93C5FD !important; }
.stSpinner > div { color: #60A5FA !important; }
.disclaimer { background: #0F172A; border: 1px solid #1E3A5F; border-left: 3px solid #F59E0B; border-radius: 0 10px 10px 0; padding: 14px 18px; font-size: 0.79rem; color: #94A3B8; margin-top: 28px; line-height: 1.6; }
.disclaimer strong { color: #FCD34D; }
.speaker-doctor { color: #60A5FA; font-weight: 600; }
.speaker-patient { color: #4DD0C4; font-weight: 600; }
.metric-row { display: flex; gap: 12px; flex-wrap: wrap; margin: 12px 0; }
.metric-chip { background: rgba(0,102,204,0.12); border: 1px solid rgba(0,102,204,0.25); border-radius: 8px; padding: 8px 16px; text-align: center; }
.metric-chip .val { font-size: 1.3rem; font-weight: 700; color: #60A5FA; }
.metric-chip .lbl { font-size: 0.7rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em; }
section[data-testid="stSidebar"] { background: #080D1A !important; border-right: 1px solid #1E3A5F !important; }
</style>
""", unsafe_allow_html=True)

# ─── Session state init ────────────────────────────────────────────────────────
for key, default in {
    "raw_transcript": "",
    "diarized_transcript": "",
    "soap_markdown": "",
    "patient_summary": "",
    "soap_pdf_bytes": b"",
    "soap_dict": {},
    "pipeline_ran": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

init_audit_log()
init_patient_sessions()

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="heydoc-header">
    <div style="font-size:2.6rem;">🏥</div>
    <div>
        <h1>HeyDoc</h1>
        <p>AI-powered medical scribe &nbsp;·&nbsp; Transcription &nbsp;·&nbsp; Speaker Diarization &nbsp;·&nbsp; SOAP Notes &nbsp;·&nbsp; Patient Summary &nbsp;·&nbsp; ICD-10 &nbsp;·&nbsp; Transmission &nbsp;·&nbsp; Sessions</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="steps-row">
    <span class="step-badge">① Audio / Transcript Input</span>
    <span class="step-badge">② Speaker Diarization</span>
    <span class="step-badge">③ SOAP Note Generation</span>
    <span class="step-badge">④ Patient Summary</span>
    <span class="step-badge">⑤ ICD-10 Codes</span>
    <span class="step-badge">⑥ Follow-Up Reminder</span>
    <span class="step-badge">⑦ Send Document</span>
    <span class="step-badge">⑧ Session Manager</span>
</div>
""", unsafe_allow_html=True)

# ─── Layout ───────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1.05], gap="large")

# ══════════════════════════════════════════════════════════
# LEFT — Input
# ══════════════════════════════════════════════════════════
with left_col:
    st.markdown('<div class="section-label">📥 Consultation Input</div>', unsafe_allow_html=True)

    recorded_audio = None
    audio_file = None

    input_tab1, input_tab2, input_tab3 = st.tabs(["🎙️ Record Audio", "📂 Upload Audio", "📝 Paste Transcript"])

    with input_tab1:
        recorded_audio = st.audio_input("Record consultation directly from your microphone", key="mic_recorder")
        if recorded_audio:
            st.audio(recorded_audio, format="audio/wav")
            st.caption("✅ Recording captured — click **▶ Get My SOAP Notes** to process it.")
        else:
            st.caption("🎤 Click the mic button above to start recording. Works directly in your browser — no extra software needed.")

    with input_tab2:
        audio_file = st.file_uploader("Upload consultation audio (WAV / MP3 / M4A)", type=["wav", "mp3", "m4a"], help="Audio will be transcribed via AI before processing.")
        if audio_file:
            st.audio(audio_file)
        st.caption("📁 Upload a pre-recorded consultation file.")

    with input_tab3:
        transcript_input = st.text_area("Paste raw consultation transcript", value=SAMPLE_TRANSCRIPT, height=240, placeholder="Doctor: How are you feeling today?\nPatient: I've had chest pain for 3 days...")
        st.caption("💡 A sample transcript is pre-loaded — click **▶ Run Pipeline** to try it instantly.")

    col_run, col_clear = st.columns([2, 1])
    with col_run:
        run_clicked = st.button("▶ Get My SOAP Notes", type="primary", use_container_width=True)
    with col_clear:
        clear_clicked = st.button("✕ Clear", type="secondary", use_container_width=True)

    if clear_clicked:
        st.session_state.raw_transcript = ""
        st.session_state.diarized_transcript = ""
        st.session_state.soap_markdown = ""
        st.session_state.patient_summary = ""
        st.session_state.soap_pdf_bytes = b""
        st.session_state.soap_dict = {}
        st.session_state.pipeline_ran = False
        for k in ["icd10_codes", "followup_reminder"]:
            if k in st.session_state:
                del st.session_state[k]
        if "mic_recorder" in st.session_state:
            del st.session_state["mic_recorder"]
        st.rerun()

    if run_clicked:
        active_audio = recorded_audio if recorded_audio is not None else (audio_file if audio_file is not None else None)
        try:
            with st.spinner("Running transcription → diarization → SOAP generation → patient summary…"):
                (
                    st.session_state.raw_transcript,
                    st.session_state.diarized_transcript,
                    st.session_state.soap_markdown,
                    st.session_state.patient_summary,
                    st.session_state.soap_pdf_bytes,
                    st.session_state.soap_dict,
                ) = run_pipeline(active_audio, transcript_input)
            st.session_state.pipeline_ran = True
            log_event("GENERATED", "Patient", {"source": "pipeline", "provider": "—", "message_id": "—"})
            st.success("✅ Pipeline completed successfully.")
        except Exception as exc:
            st.error(f"❌ {exc}")

    # Save to session manager
    if st.session_state.pipeline_ran:
        save_col1, save_col2 = st.columns([2, 1])
        with save_col1:
            patient_name_input = st.text_input("Patient name (to save session)", placeholder="e.g. John Doe", key="patient_name_save")
        with save_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 Save Session", key="save_session_btn"):
                save_current_to_session(patient_name_input, st.session_state.soap_dict, st.session_state.soap_pdf_bytes, st.session_state.patient_summary)
                st.success("Session saved!")

    # Quick-stats
    if st.session_state.pipeline_ran and st.session_state.diarized_transcript:
        lines = st.session_state.diarized_transcript.strip().splitlines()
        doc_turns = sum(1 for l in lines if l.startswith("DOCTOR:"))
        pat_turns = sum(1 for l in lines if l.startswith("PATIENT:"))
        words = len(st.session_state.raw_transcript.split())
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-chip"><div class="val">{doc_turns}</div><div class="lbl">Doctor turns</div></div>
            <div class="metric-chip"><div class="val">{pat_turns}</div><div class="lbl">Patient turns</div></div>
            <div class="metric-chip"><div class="val">{words}</div><div class="lbl">Words</div></div>
        </div>
        """, unsafe_allow_html=True)

    # Audit Log (collapsible)
    st.markdown("---")
    with st.expander("🗂️ Audit Log", expanded=False):
        render_audit_log_ui()

# ══════════════════════════════════════════════════════════
# RIGHT — Output (8 tabs)
# ══════════════════════════════════════════════════════════
with right_col:
    st.markdown('<div class="section-label">📤 Pipeline Output</div>', unsafe_allow_html=True)

    (out_tab1, out_tab2, out_tab3, out_tab4,
     out_tab5, out_tab6, out_tab7, out_tab8) = st.tabs([
        "🎤 Raw Transcript", "👥 Diarization", "📋 SOAP Notes", "🧑‍⚕️ Patient Summary",
        "🏷️ ICD-10", "🔔 Follow-Up", "📡 Send", "👥 Sessions",
    ])

    with out_tab1:
        if st.session_state.raw_transcript:
            st.text_area("Raw Transcript", value=st.session_state.raw_transcript, height=340, disabled=True)
        else:
            st.info("Run the pipeline to see the transcript here.")

    with out_tab2:
        if st.session_state.diarized_transcript:
            html_lines = []
            for line in st.session_state.diarized_transcript.strip().splitlines():
                if line.startswith("DOCTOR:"):
                    rest = line[len("DOCTOR:"):].strip()
                    html_lines.append(f'<p style="margin:4px 0;"><span class="speaker-doctor">DOCTOR</span><span style="color:#475569;">:</span> <span style="color:#CBD5E1;">{rest}</span></p>')
                elif line.startswith("PATIENT:"):
                    rest = line[len("PATIENT:"):].strip()
                    html_lines.append(f'<p style="margin:4px 0;"><span class="speaker-patient">PATIENT</span><span style="color:#475569;">:</span> <span style="color:#CBD5E1;">{rest}</span></p>')
                else:
                    html_lines.append(f'<p style="margin:4px 0; color:#475569;">{line}</p>')
            st.markdown(
                '<div style="background:#111827; border:1px solid #1E3A5F; border-radius:8px; padding:16px; max-height:340px; overflow-y:auto; font-size:0.84rem; line-height:1.7;">'
                + "".join(html_lines) + "</div>",
                unsafe_allow_html=True,
            )
            st.caption("Each line labeled DOCTOR or PATIENT by AI based on clinical speech patterns.")
        else:
            st.info("Run the pipeline to see the diarized conversation here.")

    with out_tab3:
        if st.session_state.soap_markdown:
            st.markdown(st.session_state.soap_markdown)
            if st.session_state.soap_pdf_bytes:
                st.download_button("⬇️ Download SOAP Note PDF", data=st.session_state.soap_pdf_bytes, file_name="soap_note.pdf", mime="application/pdf", use_container_width=True)
        else:
            st.info("Run the pipeline to generate the SOAP note here.")

    with out_tab4:
        if st.session_state.patient_summary:
            st.session_state.patient_summary = st.text_area("Patient-Friendly Visit Summary (Doctor Editable)", value=st.session_state.patient_summary, height=220)
            st.caption("✏️ Doctors can edit this AI-generated summary before sharing with the patient.")
        else:
            st.info("Run the pipeline to generate the patient summary here.")

    with out_tab5:
        if st.session_state.pipeline_ran and st.session_state.soap_dict:
            render_icd10_ui(st.session_state.soap_dict, OPENROUTER_API_KEY)
        else:
            st.info("Run the pipeline first to enable ICD-10 code suggestions.")

    with out_tab6:
        if st.session_state.pipeline_ran and st.session_state.soap_dict:
            render_followup_ui(st.session_state.soap_dict, OPENROUTER_API_KEY)
        else:
            st.info("Run the pipeline first to generate follow-up reminders.")

    with out_tab7:
        patient_name_for_send = st.session_state.get("patient_name_save", "Patient")
        render_transmission_ui(st.session_state.soap_pdf_bytes, patient_name=patient_name_for_send)

    with out_tab8:
        render_session_manager_ui()

# ─── Disclaimer ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
    <strong>⚠️ Clinical Disclaimer:</strong>
    All AI-generated notes must be reviewed and verified by a licensed clinician before use.
    This tool is an AI assistant — not a substitute for clinical judgment.
    Do not use patient-identifiable data in this demo environment.
</div>
""", unsafe_allow_html=True)
