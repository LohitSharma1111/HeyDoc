import base64
import json
import os
import tempfile
import textwrap

import openai
import streamlit as st

# ─── Config ───────────────────────────────────────────────────────────────────
MODEL = "openai/gpt-4o-mini"
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

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

# ─── API helpers ──────────────────────────────────────────────────────────────
def get_client(api_key: str):
    return openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


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
    s = soap.get("subjective", {})
    o = soap.get("objective", {})
    a = soap.get("assessment", {})
    p = soap.get("plan", {})

    def value(text):
        if text in (None, "", []):
            return "Not documented"
        return str(text).strip()

    def add_list(lines, heading, items):
        lines.append(heading)
        if items:
            for item in items:
                item = str(item).strip()
                if item:
                    lines.append(f"- {item}")
        else:
            lines.append("- Not documented")
        lines.append("")

    lines = [
        "SOAP NOTE",
        "AI-generated clinical documentation draft. Review and verify before sharing or adding to the medical record.",
        "",
        "SUBJECTIVE",
        f"Chief Complaint: {value(s.get('chief_complaint'))}",
        f"History of Present Illness: {value(s.get('history_of_present_illness'))}",
        f"Duration: {value(s.get('duration'))}",
        f"Severity: {value(s.get('severity'))}",
        "",
    ]
    add_list(lines, "Reported Symptoms", s.get("symptoms", []))
    lines.extend([
        "OBJECTIVE",
        f"Vitals: {value(o.get('vitals'))}",
        f"Physical Examination: {value(o.get('physical_exam'))}",
        "",
    ])
    add_list(lines, "Clinical Observations", o.get("observations", []))
    lines.extend(["ASSESSMENT", f"Primary Impression: {value(a.get('diagnosis'))}", ""])
    add_list(lines, "Differential Diagnoses", a.get("differential", []))
    lines.append("PLAN")
    add_list(lines, "Investigations / Orders", p.get("investigations", []))
    add_list(lines, "Medications / Treatments", p.get("medications", []))
    lines.extend([
        f"Follow-Up: {value(p.get('follow_up'))}",
        "",
        f"Patient Instructions: {value(p.get('instructions'))}",
    ])

    wrapped_lines = []
    for line in lines:
        if not line:
            wrapped_lines.append("")
            continue
        wrap_width = 82 if not line.isupper() else 90
        wrapped_lines.extend(textwrap.wrap(line, width=wrap_width) or [""])

    def pdf_escape(text):
        text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        return text.encode("latin-1", "replace").decode("latin-1")

    content = ["BT", "/F1 11 Tf", "50 780 Td", "14 TL"]
    for index, line in enumerate(wrapped_lines):
        escaped = pdf_escape(line)
        if index == 0:
            content.append(f"({escaped}) Tj")
        else:
            content.append("T*")
            content.append(f"({escaped}) Tj")
    content.append("ET")
    stream = "\n".join(content).encode("latin-1", "replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1") + stream + b"\nendstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("latin-1"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode("latin-1")
    )
    return bytes(pdf)


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

    return transcript, diarized, soap_markdown, patient_summary, soap_pdf


# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HeyDoc · AI Medical Scribe",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.stApp {
    background: #0A0F1E !important;
}

/* ── Header ── */
.heydoc-header {
    background: linear-gradient(135deg, #003A75 0%, #0066CC 55%, #00897B 100%);
    padding: 28px 36px;
    border-radius: 14px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 8px 32px rgba(0, 102, 204, 0.25);
}
.heydoc-header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: white;
    margin: 0;
    letter-spacing: -0.03em;
}
.heydoc-header p {
    color: rgba(255,255,255,0.82);
    margin: 5px 0 0;
    font-size: 0.88rem;
    line-height: 1.5;
}

/* ── Step badges ── */
.steps-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 24px;
}
.step-badge {
    background: rgba(0, 102, 204, 0.15);
    color: #60A5FA;
    border: 1px solid rgba(0, 102, 204, 0.3);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.01em;
}

/* ── Cards ── */
.section-card {
    background: #0F172A;
    border: 1px solid #1E3A5F;
    border-radius: 12px;
    padding: 22px 24px;
    margin-bottom: 18px;
}
.section-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #60A5FA;
    margin-bottom: 12px;
}

/* ── Streamlit overrides ── */
.stTextArea textarea {
    background: #111827 !important;
    color: #E2E8F0 !important;
    border: 1px solid #1E3A5F !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
}
.stTextArea textarea:focus {
    border-color: #0066CC !important;
    box-shadow: 0 0 0 3px rgba(0,102,204,0.15) !important;
}
label, .stTextArea label, .stFileUploader label {
    color: #94A3B8 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0066CC, #0052A3) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 10px 28px !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #0052A3, #003D7A) !important;
    box-shadow: 0 4px 18px rgba(0,102,204,0.35) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #60A5FA !important;
    border: 1.5px solid #1E3A5F !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #60A5FA !important;
    background: rgba(96, 165, 250, 0.05) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0F172A !important;
    border-bottom: 1px solid #1E3A5F !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #64748B !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 10px 18px !important;
}
.stTabs [aria-selected="true"] {
    color: #60A5FA !important;
    background: rgba(0,102,204,0.1) !important;
    border-bottom: 2px solid #0066CC !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: #0F172A !important;
    border: 1px solid #1E3A5F !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    padding: 20px !important;
}

/* ── Markdown output ── */
.stMarkdown h1 { color: #E2E8F0 !important; font-size: 1.3rem !important; }
.stMarkdown h2 { color: #93C5FD !important; font-size: 1.05rem !important; margin-top: 1.2em !important; }
.stMarkdown p, .stMarkdown li { color: #CBD5E1 !important; line-height: 1.7 !important; }
.stMarkdown strong { color: #E2E8F0 !important; }
.stMarkdown hr { border-color: #1E3A5F !important; }
.stMarkdown blockquote {
    border-left: 3px solid #F59E0B !important;
    background: rgba(245,158,11,0.07) !important;
    padding: 8px 14px !important;
    border-radius: 0 6px 6px 0 !important;
    color: #FCD34D !important;
}

/* ── File uploader ── */
.stFileUploader > div {
    background: #111827 !important;
    border: 1px dashed #1E3A5F !important;
    border-radius: 10px !important;
}
.stFileUploader > div:hover {
    border-color: #0066CC !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #00897B, #006B60) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    width: 100% !important;
}

/* ── Status / info boxes ── */
.stSuccess {
    background: rgba(0, 137, 123, 0.12) !important;
    border: 1px solid #00897B !important;
    border-radius: 8px !important;
    color: #4DD0C4 !important;
}
.stError {
    background: rgba(211, 47, 47, 0.1) !important;
    border: 1px solid #D32F2F !important;
    border-radius: 8px !important;
}
.stInfo {
    background: rgba(0, 102, 204, 0.1) !important;
    border: 1px solid #0066CC !important;
    border-radius: 8px !important;
    color: #93C5FD !important;
}
.stSpinner > div { color: #60A5FA !important; }

/* ── Disclaimer footer ── */
.disclaimer {
    background: #0F172A;
    border: 1px solid #1E3A5F;
    border-left: 3px solid #F59E0B;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    font-size: 0.79rem;
    color: #94A3B8;
    margin-top: 28px;
    line-height: 1.6;
}
.disclaimer strong { color: #FCD34D; }

/* ── Speaker diarization colors ── */
.speaker-doctor { color: #60A5FA; font-weight: 600; }
.speaker-patient { color: #4DD0C4; font-weight: 600; }

/* ── Metric chips ── */
.metric-row {
    display: flex; gap: 12px; flex-wrap: wrap; margin: 12px 0;
}
.metric-chip {
    background: rgba(0,102,204,0.12);
    border: 1px solid rgba(0,102,204,0.25);
    border-radius: 8px;
    padding: 8px 16px;
    text-align: center;
}
.metric-chip .val { font-size: 1.3rem; font-weight: 700; color: #60A5FA; }
.metric-chip .lbl { font-size: 0.7rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #080D1A !important;
    border-right: 1px solid #1E3A5F !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Session state init ────────────────────────────────────────────────────────
for key, default in {
    "raw_transcript": "",
    "diarized_transcript": "",
    "soap_markdown": "",
    "patient_summary": "",
    "soap_pdf_bytes": b"",
    "pipeline_ran": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="heydoc-header">
    <div style="font-size:2.6rem;">🏥</div>
    <div>
        <h1>HeyDoc</h1>
        <p>AI-powered medical scribe &nbsp;·&nbsp; Transcription &nbsp;·&nbsp; Speaker Diarization &nbsp;·&nbsp; SOAP Notes &nbsp;·&nbsp; Patient Summary</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="steps-row">
    <span class="step-badge">① Audio / Transcript Input</span>
    <span class="step-badge">② Speaker Diarization</span>
    <span class="step-badge">③ SOAP Note Generation</span>
    <span class="step-badge">④ Patient Summary</span>
</div>
""", unsafe_allow_html=True)

# ─── Layout: two columns ──────────────────────────────────────────────────────
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
        recorded_audio = st.audio_input(
            "Record consultation directly from your microphone",
            key="mic_recorder",
        )
        if recorded_audio:
            st.audio(recorded_audio, format="audio/wav")
            st.caption("✅ Recording captured — click **▶ Get My SOAP Notes** to process it.")
        else:
            st.caption("🎤 Click the mic button above to start recording. Works directly in your browser — no extra software needed.")

    with input_tab2:
        audio_file = st.file_uploader(
            "Upload consultation audio (WAV / MP3 / M4A)",
            type=["wav", "mp3", "m4a"],
            help="Audio will be transcribed via AI before processing.",
        )
        if audio_file:
            st.audio(audio_file)
        st.caption("📁 Upload a pre-recorded consultation file.")

    with input_tab3:
        transcript_input = st.text_area(
            "Paste raw consultation transcript",
            value=SAMPLE_TRANSCRIPT,
            height=240,
            placeholder="Doctor: How are you feeling today?\nPatient: I've had chest pain for 3 days...",
        )
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
        st.session_state.pipeline_ran = False
        if "mic_recorder" in st.session_state:
            del st.session_state["mic_recorder"]
        st.rerun()

    if run_clicked:
        # Recorded mic audio takes priority, then uploaded file, then transcript text
        active_audio = recorded_audio if recorded_audio is not None else (audio_file if audio_file is not None else None)
        try:
            with st.spinner("Running transcription → diarization → SOAP generation → patient summary…"):
                (
                    st.session_state.raw_transcript,
                    st.session_state.diarized_transcript,
                    st.session_state.soap_markdown,
                    st.session_state.patient_summary,
                    st.session_state.soap_pdf_bytes,
                ) = run_pipeline(active_audio, transcript_input)
            st.session_state.pipeline_ran = True
            st.success("✅ Pipeline completed successfully.")
        except Exception as exc:
            st.error(f"❌ {exc}")

    # Quick-stats (shown after run)
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

# ══════════════════════════════════════════════════════════
# RIGHT — Output
# ══════════════════════════════════════════════════════════
with right_col:
    st.markdown('<div class="section-label">📤 Pipeline Output</div>', unsafe_allow_html=True)

    out_tab1, out_tab2, out_tab3, out_tab4 = st.tabs(
        ["🎤 Raw Transcript", "👥 Diarization", "📋 SOAP Notes", "🧑‍⚕️ Patient Summary"]
    )

    with out_tab1:
        if st.session_state.raw_transcript:
            st.text_area(
                "Raw Transcript",
                value=st.session_state.raw_transcript,
                height=340,
                disabled=True,
            )
        else:
            st.info("Run the pipeline to see the transcript here.")

    with out_tab2:
        if st.session_state.diarized_transcript:
            # Colour-coded diarization
            html_lines = []
            for line in st.session_state.diarized_transcript.strip().splitlines():
                if line.startswith("DOCTOR:"):
                    rest = line[len("DOCTOR:"):].strip()
                    html_lines.append(
                        f'<p style="margin:4px 0;"><span class="speaker-doctor">DOCTOR</span>'
                        f'<span style="color:#475569;">:</span> '
                        f'<span style="color:#CBD5E1;">{rest}</span></p>'
                    )
                elif line.startswith("PATIENT:"):
                    rest = line[len("PATIENT:"):].strip()
                    html_lines.append(
                        f'<p style="margin:4px 0;"><span class="speaker-patient">PATIENT</span>'
                        f'<span style="color:#475569;">:</span> '
                        f'<span style="color:#CBD5E1;">{rest}</span></p>'
                    )
                else:
                    html_lines.append(f'<p style="margin:4px 0; color:#475569;">{line}</p>')

            st.markdown(
                f'<div style="background:#111827; border:1px solid #1E3A5F; border-radius:8px; '
                f'padding:16px; max-height:340px; overflow-y:auto; font-size:0.84rem; line-height:1.7;">'
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
                st.download_button(
                    "⬇️ Download SOAP Note PDF",
                    data=st.session_state.soap_pdf_bytes,
                    file_name="soap_note.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        else:
            st.info("Run the pipeline to generate the SOAP note here.")

    with out_tab4:
        if st.session_state.patient_summary:
            st.session_state.patient_summary = st.text_area(
                "Patient-Friendly Visit Summary (Doctor Editable)",
                value=st.session_state.patient_summary,
                height=220,
            )
            st.caption("✏️ Doctors can edit this AI-generated summary before sharing with the patient.")
        else:
            st.info("Run the pipeline to generate the patient summary here.")

# ─── Disclaimer ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
    <strong>⚠️ Clinical Disclaimer:</strong>
    All AI-generated notes must be reviewed and verified by a licensed clinician before use.
    This tool is an AI assistant — not a substitute for clinical judgment.
    Do not use patient-identifiable data in this demo environment.
</div>
""", unsafe_allow_html=True)