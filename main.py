import streamlit as st

st.set_page_config(
    page_title="BitDoc · Medical Scribe",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── HIPAA FIX 5: Auto-expiry (5-minute inactivity timeout) ───────────────────
import time

if "last_active" not in st.session_state:
    st.session_state.last_active = time.time()

if time.time() - st.session_state.last_active > 300:  # 5 minutes
    st.session_state.clear()
    st.warning("⏱ Session expired due to inactivity. All data has been cleared for HIPAA compliance.")
    st.stop()

# Update last_active on every interaction
st.session_state.last_active = time.time()


if "splash_shown" not in st.session_state:
    st.session_state.splash_shown = True
    st.markdown('''
    <style>
    .splash-screen {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: #FFFFFF;
        z-index: 999999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        animation: fadeOutSplash 1.5s forwards;
        animation-delay: 2.5s;
        pointer-events: none;
    }
    .splash-logo {
        font-size: 5.5rem;
        margin-bottom: 25px;
        opacity: 0;
        animation: popIn 1s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards, floatLogo 3s ease-in-out infinite;
        animation-delay: 0.2s, 1.2s;
        filter: drop-shadow(0 10px 25px rgba(18, 196, 179, 0.35));
    }
    .splash-text {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 3.5rem;
        color: #12C4B3;
        opacity: 0;
        letter-spacing: 0.05em;
        font-weight: 500;
        text-shadow: 0 4px 20px rgba(18, 196, 179, 0.25);
        animation: fadeInText 1.2s ease-out forwards;
        animation-delay: 0.8s;
    }
    .splash-sub {
        font-family: 'Inter', sans-serif;
        color: #64748B;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.3em;
        margin-top: 15px;
        opacity: 0;
        animation: fadeInText 1s ease-out forwards;
        animation-delay: 1.2s;
    }
    @keyframes fadeOutSplash {
        0% { opacity: 1; pointer-events: all; }
        99% { opacity: 0; pointer-events: none; }
        100% { opacity: 0; pointer-events: none; display: none; z-index: -1; }
    }
    @keyframes fadeInText {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    @keyframes popIn {
        0% { opacity: 0; transform: scale(0.5) translateY(20px); }
        100% { opacity: 1; transform: scale(1) translateY(0); }
    }
    @keyframes floatLogo {
        0% { transform: translateY(0); }
        50% { transform: translateY(-10px); filter: drop-shadow(0 15px 35px rgba(18, 196, 179, 0.5)); }
        100% { transform: translateY(0); }
    }
    body:has(.splash-screen) { overflow: hidden !important; }
    </style>
    <div class="splash-screen">
        <div class="splash-logo">🩺</div>
        <div class="splash-text">BitDoc</div>
        <div class="splash-sub">Medical Scribe</div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;700&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20,400,0,0&display=swap');

:root {
    --bg:       #F8FAFC;
    --surface:  #FFFFFF;
    --border:   #E2E8F0;
    --border-hi:#CBD5E1;
    --teal:     #12C4B3;
    --teal-dim: #0D9488;
    --ink:      #0F172A;
    --ink-2:    #334155;
    --ink-3:    #64748B;
    --blue:     #3B82F6;
    --sb-bg:    #0B1220;
    --sb-surface:#111C2E;
    --sb-border:#1E293B;
    --sb-ink:   #F8FAFC;
    --sb-ink-2: #94A3B8;
    --sb-ink-3: #64748B;
    --r:        16px;
    --r-sm:     10px;
}

*, html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif !important;
    -webkit-font-smoothing: antialiased !important;
}

.stApp { background: var(--bg) !important; color: var(--ink) !important; min-height: 100vh; }

[data-testid="stExpanderToggleIcon"] { display: none !important; }

header[data-testid="stHeader"] {
    background: rgba(248, 250, 252, 0.9) !important;
    backdrop-filter: blur(10px);
}
header[data-testid="stHeader"] button[kind="header"] {
    width: 2.5rem !important;
    height: 2.5rem !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
    box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06) !important;
    color: var(--ink-2) !important;
}
header[data-testid="stHeader"] button[kind="header"]:hover {
    border-color: var(--border-hi) !important;
    background: #F8FAFC !important;
}
div[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] button,
header[data-testid="stHeader"] button[aria-label*="sidebar" i],
section[data-testid="stSidebar"] button[aria-label*="sidebar" i] {
    display: none !important;
}

section[data-testid="stSidebar"] {
    background: var(--sb-bg) !important;
    border-right: 1px solid var(--sb-border) !important;
    width: 240px !important;
}
section[data-testid="stSidebar"] .block-container { padding: 2rem 1.2rem !important; }
section[data-testid="stSidebar"] > div { background: transparent !important; }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: var(--sb-ink-2) !important;
}

.brand-block {
    display: flex; align-items: center; gap: 14px;
    padding: 12px 14px 18px;
    border-bottom: 1px solid var(--sb-border);
    margin-bottom: 20px;
}
.brand-icon {
    width: 38px; height: 38px; border-radius: 10px;
    background: var(--teal); color: #041F1C;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; box-shadow: 0 4px 12px rgba(18,196,179,0.3);
}
.brand-name { font-size: 1.25rem; color: var(--sb-ink); letter-spacing: 0.02em; line-height: 1.1; font-weight: 800; }
.brand-sub { font-size: 0.6rem; color: var(--sb-ink-3); text-transform: uppercase; letter-spacing: 0.14em; font-weight: 700; margin-top: 4px; }

.stRadio > div { gap: 8px !important; }
.stRadio > div > label {
    background: var(--teal) !important;
    border: 1px solid var(--teal) !important;
    border-radius: var(--r-sm) !important;
    padding: 10px 14px !important;
    cursor: pointer !important;
    color: #FFFFFF !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
    opacity: 0.8;
}
.stRadio > div > label:hover {
    background: var(--teal-dim) !important;
    border-color: var(--teal-dim) !important;
    color: #FFFFFF !important;
    opacity: 1;
}
.stRadio > div > label:has(input:checked) {
    background: var(--teal-dim) !important;
    border-color: var(--teal-dim) !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    opacity: 1;
    box-shadow: 0 0 0 2px rgba(18,196,179,0.2) !important;
}
.stRadio > div > label > div:first-child { display: none !important; }

section[data-testid="stSidebar"] .stRadio > div > label {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: var(--sb-ink-2) !important;
    opacity: 1;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: var(--sb-surface) !important;
    border-color: transparent !important;
    color: var(--sb-ink) !important;
}
section[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
    background: rgba(18,196,179,0.1) !important;
    border-color: transparent !important;
    color: var(--teal) !important;
    font-weight: 700 !important;
    box-shadow: none !important;
}

.nav-section-label { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.16em; color: var(--sb-ink-3); padding: 16px 14px 8px; font-weight: 800; }

.status-pill { display: flex; align-items: center; gap: 8px; padding: 9px 12px; border-radius: 8px; font-size: 0.72rem; font-weight: 700; border: 1px solid; margin: 8px 6px 0; text-transform: uppercase; letter-spacing: 0.06em; }
.status-pill.ready { background: rgba(16,185,129,0.08); border-color: rgba(16,185,129,0.3); color: #10B981; }
.status-pill.empty { background: rgba(255,255,255,0.02); border-color: var(--sb-border); color: var(--sb-ink-3); }
.status-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.status-dot.ready { background: #10B981; box-shadow: 0 0 8px #10B981; animation: livepulse 2s infinite; }
.status-dot.empty { background: var(--sb-ink-3); }

.hipaa-badge {
    display: flex; align-items: center; gap: 8px; padding: 8px 12px;
    background: rgba(16,185,129,0.06); border: 1px solid rgba(16,185,129,0.2);
    border-radius: 8px; margin: 12px 6px 0; font-size: 0.68rem; font-weight: 800;
    color: #10B981; text-transform: uppercase; letter-spacing: 0.08em;
}
.session-timer {
    display: flex; align-items: center; gap: 8px; padding: 8px 12px;
    background: rgba(245,158,11,0.06); border: 1px solid rgba(245,158,11,0.2);
    border-radius: 8px; margin: 6px 6px 0; font-size: 0.68rem; font-weight: 700;
    color: #D97706; text-transform: uppercase; letter-spacing: 0.06em;
}

.block-container { padding: 1.8rem 2.2rem 3rem !important; max-width: none !important; }

.ph-wrap { display: flex; align-items: center; gap: 14px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--r); padding: 14px 20px; margin-bottom: 24px; margin-top: -10px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
.ph-icon-wrap { width: 40px; height: 40px; border-radius: 10px; border: 1px solid var(--border-hi); background: #F8FAFC; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0; color: var(--ink-2); }
.ph-title { font-size: 1.2rem; font-weight: 800; color: var(--ink); letter-spacing: -0.01em; margin: 0; }
.ph-sub { font-size: 0.75rem; color: var(--ink-3); margin: 2px 0 0; font-weight: 500; }

.stTabs [data-baseweb="tab-list"] { background: #F1F5F9 !important; border: none !important; border-radius: 12px !important; gap: 0 !important; padding: 4px !important; margin-bottom: 20px !important; width: 100% !important; display: flex !important; }
.stTabs [data-baseweb="tab"] { flex: 1 !important; justify-content: center !important; border: 0 !important; border-radius: 8px !important; color: var(--ink-3) !important; font-size: 0.85rem !important; padding: 10px 14px !important; font-weight: 700 !important; background: transparent !important; white-space: nowrap !important; }
.stTabs [data-baseweb="tab"]:hover { color: var(--ink-2) !important; }
.stTabs [aria-selected="true"] { background: var(--surface) !important; color: var(--ink) !important; border: 1px solid var(--border) !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important; }
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; border: none !important; padding: 0 !important; }

.stButton > button { border-radius: 9px !important; font-size: 0.86rem !important; font-weight: 800 !important; padding: 11px 20px !important; background: var(--surface) !important; color: var(--ink-2) !important; border: 1px solid var(--border-hi) !important; transition: all 0.2s ease !important; box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important; }
.stButton > button:hover { background: var(--bg) !important; color: var(--ink) !important; border-color: var(--border-hi) !important; }
.stButton > button[kind="primary"] { background: var(--teal) !important; color: white !important; border: 1px solid var(--teal) !important; }
.stButton > button[kind="primary"]:hover { background: var(--teal-dim) !important; border-color: var(--teal-dim) !important; }
[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button { background: var(--ink) !important; color: white !important; border: 1px solid var(--ink) !important; }
[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button:hover { background: var(--ink-2) !important; }
.stDownloadButton > button {
    background: var(--teal) !important;
    color: #FFFFFF !important;
    border: 1px solid var(--teal) !important;
    font-weight: 800 !important;
}
.stDownloadButton > button:hover {
    background: var(--teal-dim) !important;
    border-color: var(--teal-dim) !important;
    color: #FFFFFF !important;
}

.metric-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r); padding: 18px 16px; text-align: left; transition: border-color 0.2s ease; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
.metric-card:hover { border-color: var(--border-hi); }
.metric-val { font-size: 2rem; font-weight: 800; color: var(--ink); letter-spacing: -0.04em; margin: 8px 0 2px; }
.metric-lbl { font-size: 0.72rem; color: var(--ink-3); text-transform: uppercase; font-weight: 800; letter-spacing: 0.1em; }

.stTextArea textarea, .stTextInput input, .stSelectbox select { background: var(--surface) !important; border: 1px solid var(--border-hi) !important; border-radius: 9px !important; color: var(--ink) !important; font-size: 0.88rem !important; transition: border-color 0.2s ease !important; padding: 12px 14px !important; box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important; }
.stTextArea textarea:focus, .stTextInput input:focus { border-color: var(--teal) !important; box-shadow: 0 0 0 3px rgba(18,196,179,0.12) !important; outline: none !important; }
.stTextArea textarea:disabled { color: #000000 !important; -webkit-text-fill-color: #000000 !important; opacity: 1 !important; }
label, .stSelectbox label { color: var(--ink-3) !important; font-size: 0.7rem !important; font-weight: 800 !important; text-transform: uppercase !important; letter-spacing: 0.14em !important; margin-bottom: 6px !important; }

.session-list-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r); margin-top: 14px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }

.sp-line {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 7px 4px;
    border-bottom: 1px solid rgba(0,0,0,0.04);
}
.sp-line:last-child { border-bottom: none; }
.sp-tag {
    flex-shrink: 0;
    font-size: 0.65rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 3px 8px;
    border-radius: 5px;
    margin-top: 1px;
    min-width: 32px;
    text-align: center;
}
.sp-tag.doc {
    background: rgba(18,196,179,0.12);
    color: #0D9488;
    border: 1px solid rgba(18,196,179,0.3);
}
.sp-tag.pat {
    background: rgba(59,130,246,0.1);
    color: #2563EB;
    border: 1px solid rgba(59,130,246,0.25);
}
.sp-sep {
    color: #CBD5E1;
    font-weight: 400;
    margin-top: 1px;
    flex-shrink: 0;
}
.sp-speech {
    color: #1E293B !important;
    font-size: 0.875rem;
    line-height: 1.55;
    flex: 1;
}

.icd-row { display: flex; align-items: center; gap: 16px; background: var(--surface); border: 1px solid var(--border); border-radius: 9px; padding: 14px 18px; margin-bottom: 10px; transition: all 0.2s ease; }
.icd-row:hover { border-color: var(--border-hi); background: var(--bg); }
.icd-code { font-family: 'JetBrains Mono', monospace !important; font-size: 0.88rem; color: var(--teal-dim); font-weight: 700; width: 68px; }
.icd-desc { font-size: 0.88rem; color: var(--ink); flex: 1; }
.icd-badge { font-size: 0.67rem; padding: 3px 10px; border-radius: 20px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; }
.icd-high { background: rgba(16,185,129,0.1); color: #10B981; border: 1px solid rgba(16,185,129,0.3); }

.stAudioInput { background: var(--surface) !important; border-radius: 10px !important; border: 1px solid var(--border-hi) !important; padding: 12px !important; }
.stFileUploader > div { background: var(--surface) !important; border: 2px dashed rgba(18,196,179,0.25) !important; border-radius: 12px !important; padding: 20px !important; }

.empty-state { background: var(--surface); border: 1px dashed rgba(18,196,179,0.22); border-radius: var(--r); padding: 44px 28px; text-align: center; color: var(--ink-3); font-size: 0.9rem; transition: border-color 0.2s ease; }
.empty-state-icon { font-size: 2rem; margin-bottom: 12px; color: var(--teal); }

.warn-banner { background: rgba(245,158,11,0.06); border: 1px solid rgba(245,158,11,0.22); border-radius: 9px; padding: 10px 16px; font-size: 0.82rem; color: #D97706; margin-bottom: 20px; }
.hipaa-banner { background: rgba(16,185,129,0.05); border: 1px solid rgba(16,185,129,0.25); border-radius: 9px; padding: 10px 16px; font-size: 0.82rem; color: #059669; margin-bottom: 12px; }
.disclaimer { background: rgba(18,196,179,0.03); border: 1px solid rgba(18,196,179,0.12); border-radius: 9px; padding: 14px 18px; font-size: 0.78rem; color: var(--ink-3); margin-top: 28px; }
.disclaimer strong { color: var(--teal-dim); text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.08em; }
.bd-loading-overlay {
    position: fixed;
    inset: 0;
    background: rgba(11, 18, 32, 0.55);
    backdrop-filter: blur(3px);
    z-index: 999998;
    display: flex;
    align-items: center;
    justify-content: center;
}
.bd-loading-card {
    background: #FFFFFF;
    border: 1px solid var(--border-hi);
    border-radius: 14px;
    width: min(520px, 92vw);
    padding: 20px 22px;
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.22);
}
.bd-loading-title {
    margin: 0;
    color: var(--ink);
    font-size: 1rem;
    font-weight: 800;
}
.bd-loading-sub {
    margin: 6px 0 0;
    color: var(--ink-3);
    font-size: 0.85rem;
}
.bd-loading-track {
    margin-top: 14px;
    width: 100%;
    height: 8px;
    background: #E2E8F0;
    border-radius: 999px;
    overflow: hidden;
}
.bd-loading-bar {
    width: 38%;
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #12C4B3 0%, #0D9488 100%);
    animation: bdSlide 1.1s ease-in-out infinite alternate;
}
@keyframes bdSlide {
    from { transform: translateX(0); }
    to { transform: translateX(160%); }
}

[data-testid="stHorizontalBlock"] { gap: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
defaults = {
    "session_id": "",
    "raw_transcript": "",
    "diarized_transcript": "",
    "soap_markdown": "",
    "patient_summary": "",
    "soap_pdf_bytes": b"",
    "soap_dict": {},
    "pipeline_ran": False,
    "audit_log": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HIPAA FIX 4: Clear sensitive data helper ───────────────────────────────────
def clear_sensitive_data():
    """Wipe all PHI-adjacent data from session state."""
    phi_keys = [
        "raw_transcript",
        "diarized_transcript",
        "soap_markdown",
        "patient_summary",
        "soap_dict",
        "soap_pdf_bytes",
        "pipeline_ran",
        "session_id",
        "icd10_codes",
        "followup_reminder",
    ]
    for key in phi_keys:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.pipeline_ran = False
    st.session_state.soap_pdf_bytes = b""
    st.session_state.soap_dict = {}

# ── HIPAA FIX 1: Generate anonymous session ID ─────────────────────────────────
def new_session_id():
    import random
    return f"SESSION-{random.randint(10000, 99999)}"

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand-block">
        <div class="brand-icon">🩺</div>
        <div>
            <div class="brand-name">BITDOC</div>
            <div class="brand-sub">Medical Scribe</div>
        </div>
    </div>
    <div class="nav-section-label">Workspace</div>
    """, unsafe_allow_html=True)

    nav_options = [
        "Record & Transcribe",
        "SOAP Note",
        "Patient Summary",
        "ICD-10 Codes",
        "Follow-Up",
        "Send Document",
        "Audit Log",
    ]
    page = st.radio("nav", nav_options, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.pipeline_ran:
        st.markdown("""
        <div class="status-pill ready">
            <div class="status-dot ready"></div>
            Note ready
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-pill empty">
            <div class="status-dot empty"></div>
            No note yet
        </div>""", unsafe_allow_html=True)

    elapsed = int(time.time() - st.session_state.last_active)
    remaining = max(0, 300 - elapsed)
    mins, secs = divmod(remaining, 60)
    st.markdown(f"""
    <div class="hipaa-badge">🔒 HIPAA Mode Active</div>
    <div class="session-timer">⏱ Auto-clear in {mins}m {secs:02d}s</div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑 Clear Session Now", use_container_width=True):
        clear_sensitive_data()
        st.session_state.audit_log = []
        st.rerun()

# ── Imports & backend ─────────────────────────────────────────────────────────
import base64, csv, datetime, io, json, os, random, smtplib, tempfile
from email.message import EmailMessage
import requests, openai
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)

MODEL              = "openai/gpt-4o-mini"
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
OPENAI_API_KEY     = st.secrets.get("OPENAI_API_KEY", "")
BASE_URL           = st.secrets.get("BASE_URL", "")
API_KEY            = st.secrets.get("API_KEY", "")

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

kno2_headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def get_client(api_key):
    return openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

def transcribe_with_whisper(audio_path, api_key):
    client = get_client(api_key)
    with open(audio_path, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()
    r = client.chat.completions.create(
        model="google/gemini-3.1-flash-lite-preview",
        messages=[{"role":"user","content":[
            {"type":"text","text":"Transcribe this audio exactly."},
            {"type":"input_audio","input_audio":{"data":audio_b64,"format":"wav"}},
        ]}])
    return r.choices[0].message.content

def diarize_transcript(transcript, api_key):
    client = get_client(api_key)
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
    r = client.chat.completions.create(model=MODEL, messages=[{"role":"user","content":prompt}], max_tokens=2000)
    return r.choices[0].message.content.strip()

def generate_soap(diarized, api_key):
    client = get_client(api_key)
    prompt = f"""You are an expert medical scribe. Generate a SOAP note from this conversation.
Return ONLY valid JSON (no markdown):
{{"subjective":{{"chief_complaint":"...","history_of_present_illness":"...","symptoms":[],"duration":"...","severity":"..."}},"objective":{{"vitals":"...","physical_exam":"...","observations":[]}},"assessment":{{"diagnosis":"...","differential":[]}},"plan":{{"investigations":[],"medications":[],"follow_up":"...","instructions":"..."}}}}
Conversation:\n{diarized}"""
    r = client.chat.completions.create(model=MODEL, messages=[{"role":"user","content":prompt}], max_tokens=1500)
    raw = r.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
    return json.loads(raw)

def generate_patient_summary(soap, api_key):
    client = get_client(api_key)
    prompt = f"""Write a short, warm, patient-friendly visit summary (under 150 words).
Use simple language, 2nd person. Start with "You came in today..."
Do NOT include any patient name or identifying information.
SOAP:\n{json.dumps(soap,indent=2)}"""
    r = client.chat.completions.create(model=MODEL, messages=[{"role":"user","content":prompt}], max_tokens=400)
    return r.choices[0].message.content.strip()

def format_soap_markdown(soap):
    s,o,a,p = soap.get("subjective",{}),soap.get("objective",{}),soap.get("assessment",{}),soap.get("plan",{})
    def v(x): return str(x).strip() if x not in (None,"",[]) else "Not documented"
    def bl(items): return "\n".join(f"- {i}" for i in items) if items else "- Not documented"
    return f"""## S — Subjective
**Chief Complaint:** {v(s.get('chief_complaint'))}

**History:** {v(s.get('history_of_present_illness'))}

**Duration:** {v(s.get('duration'))}  ·  **Severity:** {v(s.get('severity'))}

**Symptoms:**
{bl(s.get('symptoms',[]))}

---
## O — Objective
**Vitals:** {v(o.get('vitals'))}

**Examination:** {v(o.get('physical_exam'))}

**Observations:**
{bl(o.get('observations',[]))}

---
## A — Assessment
**Primary Diagnosis:** {v(a.get('diagnosis'))}

**Differential:**
{bl(a.get('differential',[]))}

---
## P — Plan
**Investigations:**
{bl(p.get('investigations',[]))}

**Medications:**
{bl(p.get('medications',[]))}

**Follow-Up:** {v(p.get('follow_up'))}

**Instructions:** {v(p.get('instructions'))}
"""

# ══════════════════════════════════════════════════════════════════════════════
# PDF GENERATION — BitDoc themed, BITDOC header + footer on every page
# ══════════════════════════════════════════════════════════════════════════════

def create_soap_pdf_bytes(soap):
    s = soap.get("subjective", {})
    o = soap.get("objective", {})
    a = soap.get("assessment", {})
    p = soap.get("plan", {})

    # ── Brand palette matching app CSS vars
    DARK_BG    = colors.HexColor("#0B1220")
    TEAL       = colors.HexColor("#12C4B3")
    TEAL_DIM   = colors.HexColor("#0D9488")
    INK        = colors.HexColor("#F8FAFC")
    INK3       = colors.HexColor("#64748B")
    CARD_BG    = colors.HexColor("#FFFFFF")
    CARD_BDR   = colors.HexColor("#E2E8F0")
    AMBER_DIM  = colors.HexColor("#D97706")
    SECTION_BG = colors.HexColor("#0F172A")

    W, H = letter

    def val(x):
        return str(x).strip() if x not in (None, "", []) else "Not documented"

    def bullet_items(items):
        if not items:
            return [Paragraph("• Not documented", s_bul)]
        return [Paragraph(f"• {str(i).strip()}", s_bul) for i in items if str(i).strip()]

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=0.55 * inch, rightMargin=0.55 * inch,
        topMargin=0.90 * inch, bottomMargin=0.65 * inch,
        title="SOAP Note — BitDoc",
        author="BitDoc AI Medical Scribe",
    )

    # ── Canvas callback: draws branded header + footer on every page
    def draw_page_chrome(canvas, doc):
        canvas.saveState()

        # ── HEADER: dark navy bar across the top
        canvas.setFillColor(DARK_BG)
        canvas.rect(0, H - 0.72 * inch, W, 0.72 * inch, fill=1, stroke=0)

        # Teal left accent stripe
        canvas.setFillColor(TEAL)
        canvas.rect(0, H - 0.72 * inch, 0.22 * inch, 0.72 * inch, fill=1, stroke=0)

        # "BITDOC" wordmark (left)
        canvas.setFillColor(TEAL)
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawString(0.36 * inch, H - 0.43 * inch, "BITDOC")

        # "AI Medical Scribe" subtitle under wordmark
        canvas.setFillColor(INK3)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(0.36 * inch, H - 0.585 * inch, "AI Medical Scribe")

        # "SOAP NOTE" centered
        canvas.setFillColor(INK)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawCentredString(W / 2, H - 0.435 * inch, "SOAP NOTE")

        # Teal underline accent beneath centered title
        canvas.setStrokeColor(TEAL)
        canvas.setLineWidth(1.2)
        title_w = 72  # approx width of "SOAP NOTE" at 11pt
        canvas.line(W / 2 - 36, H - 0.50 * inch, W / 2 + 36, H - 0.50 * inch)

        # Date + page number (right)
        canvas.setFillColor(INK3)
        canvas.setFont("Helvetica", 7.5)
        today_str = datetime.date.today().strftime("%b %d, %Y")
        canvas.drawRightString(W - 0.45 * inch, H - 0.385 * inch, today_str)
        canvas.drawRightString(W - 0.45 * inch, H - 0.545 * inch, f"Page {doc.page}")

        # ── FOOTER: dark navy bar across the bottom
        canvas.setFillColor(DARK_BG)
        canvas.rect(0, 0, W, 0.42 * inch, fill=1, stroke=0)

        # Thin teal top line on footer
        canvas.setFillColor(TEAL)
        canvas.rect(0, 0.42 * inch, W, 0.025 * inch, fill=1, stroke=0)

        # Thin teal bottom line (very base)
        canvas.setFillColor(TEAL)
        canvas.rect(0, 0, W, 0.025 * inch, fill=1, stroke=0)

        # Footer disclaimer text
        canvas.setFillColor(INK3)
        canvas.setFont("Helvetica", 6.5)
        canvas.drawCentredString(
            W / 2, 0.155 * inch,
            "BitDoc AI Medical Scribe  ·  AI-generated draft — must be reviewed by a licensed clinician before clinical use"
        )

        canvas.restoreState()

    # ── Paragraph styles
    base_styles = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name, parent=base_styles["Normal"], **kw)

    s_lbl = ps("LBL",
        fontSize=6.5, leading=9,
        textColor=INK3, fontName="Helvetica-Bold",
        spaceBefore=0, spaceAfter=2,
    )
    s_val = ps("VAL",
        fontSize=9, leading=13.5,
        textColor=colors.HexColor("#1E293B"), fontName="Helvetica",
        spaceAfter=4,
    )
    s_bul = ps("BUL",
        fontSize=9, leading=13,
        textColor=colors.HexColor("#1E293B"), fontName="Helvetica",
        leftIndent=4, spaceAfter=2,
    )
    s_warn = ps("WRN",
        fontSize=7.5, leading=11,
        textColor=AMBER_DIM, fontName="Helvetica-Oblique",
        alignment=TA_CENTER,
    )

    # ── Section header: dark badge letter + title on dark bar, teal underline
    def section_header(badge, title, accent=SECTION_BG):
        badge_para = Paragraph(
            f"<b>{badge}</b>",
            ParagraphStyle("BDG", fontSize=13, textColor=TEAL,
                           fontName="Helvetica-Bold", alignment=TA_CENTER),
        )
        title_para = Paragraph(
            f"<b>{title}</b>",
            ParagraphStyle("TTL", fontSize=9.5, textColor=INK,
                           fontName="Helvetica-Bold", alignment=TA_LEFT),
        )
        t = Table([[badge_para, title_para]], colWidths=[0.42 * inch, None])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), accent),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING",   (0, 0), (0,  0),  6),
            ("RIGHTPADDING",  (0, 0), (0,  0),  4),
            ("LEFTPADDING",   (1, 0), (1,  0),  12),
            ("TOPPADDING",    (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("LINEBELOW",     (0, 0), (-1, -1), 1.2, TEAL),
        ]))
        return t

    # ── White card with stacked label / value pairs
    def info_card(pairs):
        rows = []
        for lbl, value in pairs:
            rows.append([Paragraph(lbl, s_lbl)])
            rows.append([Paragraph(val(value), s_val)])
        t = Table(rows, colWidths=[doc.width])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), CARD_BG),
            ("BOX",           (0, 0), (-1, -1), 0.5, CARD_BDR),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ]))
        return t

    # ── White card with optional label + bullet list
    def bullet_card(items, label=None):
        content = []
        if label:
            content.append(Paragraph(label, s_lbl))
        content += bullet_items(items)
        t = Table([[c] for c in content], colWidths=[doc.width])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), CARD_BG),
            ("BOX",           (0, 0), (-1, -1), 0.5, CARD_BDR),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ]))
        return t

    def rule():
        return HRFlowable(
            width="100%", thickness=0.5, color=CARD_BDR,
            spaceAfter=10, spaceBefore=10,
        )

    # ── Build story
    story = []

    # Warning banner (amber)
    warn_t = Table(
        [[Paragraph("⚠  AI-generated draft — verify all details before clinical use or sharing", s_warn)]],
        colWidths=[doc.width],
    )
    warn_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#FFFBEB")),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#FCD34D")),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
    ]))
    story.append(warn_t)
    story.append(Spacer(1, 14))

    # ── S — SUBJECTIVE
    story.append(KeepTogether([
        section_header("S", "SUBJECTIVE"),
        Spacer(1, 8),
        info_card([
            ("Chief Complaint",              s.get("chief_complaint")),
            ("History of Present Illness",   s.get("history_of_present_illness")),
        ]),
        Spacer(1, 8),
        info_card([
            ("Duration", s.get("duration")),
            ("Severity", s.get("severity")),
        ]),
        Spacer(1, 8),
        bullet_card(s.get("symptoms", []), label="Symptoms"),
    ]))
    story.append(Spacer(1, 10))
    story.append(rule())

    # ── O — OBJECTIVE
    story.append(KeepTogether([
        section_header("O", "OBJECTIVE", accent=colors.HexColor("#0A1F1E")),
        Spacer(1, 8),
        info_card([
            ("Vitals",               o.get("vitals")),
            ("Physical Examination", o.get("physical_exam")),
        ]),
        Spacer(1, 8),
        bullet_card(o.get("observations", []), label="Clinical Observations"),
    ]))
    story.append(Spacer(1, 10))
    story.append(rule())

    # ── A — ASSESSMENT
    story.append(KeepTogether([
        section_header("A", "ASSESSMENT", accent=colors.HexColor("#0C1A0F")),
        Spacer(1, 8),
        info_card([("Primary Diagnosis", a.get("diagnosis"))]),
        Spacer(1, 8),
        bullet_card(a.get("differential", []), label="Differential Diagnoses"),
    ]))
    story.append(Spacer(1, 10))
    story.append(rule())

    # ── P — PLAN
    story.append(section_header("P", "PLAN", accent=colors.HexColor("#0E0F1A")))
    story.append(Spacer(1, 8))
    story.append(bullet_card(p.get("investigations", []), label="Investigations / Orders"))
    story.append(Spacer(1, 8))
    story.append(bullet_card(p.get("medications", []),    label="Medications"))
    story.append(Spacer(1, 8))
    story.append(info_card([
        ("Follow-Up",            p.get("follow_up")),
        ("Patient Instructions", p.get("instructions")),
    ]))

    doc.build(story, onFirstPage=draw_page_chrome, onLaterPages=draw_page_chrome)
    return buf.getvalue()


def run_pipeline(audio_file, transcript_text):
    if not OPENROUTER_API_KEY.strip():
        raise ValueError("Set OPENROUTER_API_KEY in .streamlit/secrets.toml")
    transcript, temp = "", None
    if audio_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.getbuffer()); temp = tmp.name
        transcript = transcribe_with_whisper(temp, OPENAI_API_KEY)
    elif transcript_text.strip():
        transcript = transcript_text.strip()
    else:
        raise ValueError("Provide an audio file or transcript.")
    diarized = diarize_transcript(transcript, OPENROUTER_API_KEY)
    soap     = generate_soap(diarized, OPENROUTER_API_KEY)
    md       = format_soap_markdown(soap)
    summary  = generate_patient_summary(soap, OPENROUTER_API_KEY)
    pdf      = create_soap_pdf_bytes(soap)
    if temp:
        try: os.unlink(temp)
        except: pass
    return transcript, diarized, md, summary, pdf, soap

def suggest_icd10_codes(soap, api_key):
    client = get_client(api_key)
    a,sv = soap.get("assessment",{}),soap.get("subjective",{})
    prompt = f"""Suggest 3 ICD-10 codes. Return ONLY JSON array:
[{{"code":"X00.0","description":"...","confidence":"high|medium|low"}}]
Diagnosis: {a.get('diagnosis')} Differential: {a.get('differential',[])}
Complaint: {sv.get('chief_complaint')} Symptoms: {sv.get('symptoms',[])}"""
    try:
        r = client.chat.completions.create(model=MODEL,messages=[{"role":"user","content":prompt}],max_tokens=400)
        raw = r.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
        return json.loads(raw)
    except:
        return [{"code":"—","description":"Could not generate codes","confidence":"low"}]

def generate_followup_reminder(soap, api_key):
    client = get_client(api_key)
    pl = soap.get("plan",{})
    prompt = f"""Write a brief friendly SMS-style follow-up reminder (<120 words).
Start with "Hello," (no name). Include next steps, return date, who to call.
Do NOT include any patient name or identifying information.
Follow-up: {pl.get('follow_up')} Tests: {pl.get('investigations',[])} Meds: {pl.get('medications',[])}"""
    try:
        r = client.chat.completions.create(model=MODEL,messages=[{"role":"user","content":prompt}],max_tokens=200)
        return r.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate reminder: {e}"

AUDIT_LOG_FIELDS = [
    "timestamp", "action", "session_id", "patient", "source",
    "provider", "message_id", "recipient_type", "attempts",
    "status", "error", "meta",
]

def _audit_val(value):
    if value is None:
        return "—"
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=True)
    text = str(value).strip()
    return text if text else "—"

def log_event(action, details=None):
    session_id = st.session_state.get("session_id", "UNKNOWN")
    details = details or {}
    action_text = str(action).strip().upper() if action is not None else "UNKNOWN"
    entry = {k: "—" for k in AUDIT_LOG_FIELDS}
    entry.update({
        "timestamp":  datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "action":     action_text or "UNKNOWN",
        "session_id": _audit_val(session_id if session_id else "UNKNOWN"),
        "patient":    "anonymous",
    })
    allowed = set(AUDIT_LOG_FIELDS) - {"timestamp", "action", "session_id", "patient"}
    extras = {}
    for key, value in details.items():
        if key in allowed:
            entry[key] = _audit_val(value)
        else:
            extras[key] = value
    if extras:
        entry["meta"] = _audit_val(extras)
    st.session_state.audit_log.append(entry)

def send_via_mock(pdf_bytes, recipient):
    time.sleep(0.5)
    ok = random.random() > 0.2
    return {"success": ok, "message_id": f"MOCK-{random.randint(10000,99999)}", "provider": "mock",
            "error": None if ok else "Simulated failure"}

def send_via_kno2(pdf_bytes, fax_number):
    try:
        r = requests.post(f"{BASE_URL}/messages", headers=kno2_headers,
                          json={"to":[{"type":"Fax","value":fax_number}],"subject":"SOAP Note","body":"Medical document attached"})
        mid = r.json()["id"]
        requests.post(f"{BASE_URL}/messages/{mid}/attachments",
                      headers={"Authorization":f"Bearer {API_KEY}"},
                      files={"file":("soap.pdf",pdf_bytes,"application/pdf")})
        sr = requests.post(f"{BASE_URL}/messages/{mid}/send", headers=kno2_headers)
        return {"success":sr.status_code==200,"message_id":mid,"provider":"kno2","error":None if sr.status_code==200 else "Send failed"}
    except Exception as e:
        return {"success":False,"message_id":None,"provider":"kno2","error":str(e)}

def send_via_email(pdf_bytes, to_email, smtp_host, smtp_port, sender_email, sender_password,
                   subject=None, body=None, attach_pdf=True, attachment_name=None,
                   provider_tag="email"):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject or f"SOAP Note — {datetime.date.today()}"
        msg["From"] = sender_email; msg["To"] = to_email
        msg.set_content(body or "SOAP note attached.\nGenerated by BitDoc AI Medical Scribe. Review before clinical use.")
        if attach_pdf and pdf_bytes:
            msg.add_attachment(
                pdf_bytes, maintype="application", subtype="pdf",
                filename=attachment_name or f"soap_{datetime.date.today()}.pdf",
            )
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as smtp:
            smtp.login(sender_email, sender_password); smtp.send_message(msg)
        return {"success":True,"message_id":f"EMAIL-{random.randint(10000,99999)}","provider":provider_tag,"error":None}
    except Exception as e:
        return {"success":False,"message_id":None,"provider":provider_tag,"error":str(e)}

def send_with_retry(send_fn, retries=2, delay=1.0, **kwargs):
    last = {}
    for i in range(1, retries+1):
        r = send_fn(**kwargs)
        if r["success"]: r["attempts"]=i; return r
        last = r
        if i < retries: time.sleep(delay)
    last["attempts"] = retries; return last

def clear_transient_contact_fields():
    for key in ["patient_email_input","patient_phone_input","sender_email_input","sender_password_input"]:
        if key in st.session_state:
            st.session_state[key] = ""

# ── Page helpers ───────────────────────────────────────────────────────────────
def page_header(icon, title, subtitle=""):
    st.markdown(f"""
    <div class="ph-wrap">
        <div class="ph-icon-wrap">{icon}</div>
        <div>
            <div class="ph-title">{title}</div>
            {'<div class="ph-sub">' + subtitle + '</div>' if subtitle else ''}
        </div>
    </div>""", unsafe_allow_html=True)

def empty_state(msg="Generate a note first to use this page."):
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-icon">✦</div>
        <div>{msg}</div>
    </div>""", unsafe_allow_html=True)

def hipaa_banner(msg):
    st.markdown(f'<div class="hipaa-banner">🔒 {msg}</div>', unsafe_allow_html=True)

def show_loading_screen(message="Generating SOAP note..."):
    st.markdown(f"""
    <div class="bd-loading-overlay">
        <div class="bd-loading-card">
            <p class="bd-loading-title">{message}</p>
            <p class="bd-loading-sub">Transcribing, structuring SOAP Notes. Please wait.</p>
            <div class="bd-loading-track"><div class="bd-loading-bar"></div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════

# ── PAGE 1: Record & Transcribe ───────────────────────────────────────────────
if page == "Record & Transcribe":
    page_header("🎙", "Record & Transcribe",
                "Capture audio or paste a transcript to generate your SOAP note")

    hipaa_banner("No patient names or identifiers are stored. Each session uses an anonymous ID only.")

    t1, t2, t3 = st.tabs(["Record", "Upload File", "Paste Transcript"])
    recorded_audio = None
    audio_file = None

    with t1:
        st.markdown("<br>", unsafe_allow_html=True)
        recorded_audio = st.audio_input("Record audio", key="mic_input", label_visibility="collapsed")
        if recorded_audio:
            st.audio(recorded_audio, format="audio/wav")
            st.caption("✓ Recording captured — click Generate below")
        else:
            st.caption("Click the microphone to begin recording")

    with t2:
        st.markdown("<br>", unsafe_allow_html=True)
        audio_file = st.file_uploader("Upload audio file", type=["wav","mp3","m4a"], label_visibility="collapsed")
        if audio_file:
            st.audio(audio_file)
            st.caption("✓ File ready")
        else:
            st.caption("Accepts WAV · MP3 · M4A")

    with t3:
        st.markdown("<br>", unsafe_allow_html=True)
        transcript_input = st.text_area(
            "Transcript input", value=SAMPLE_TRANSCRIPT, height=260,
            placeholder="Doctor: How are you feeling?\nPatient: I've had chest pain...",
            label_visibility="collapsed")
        st.caption("Sample transcript loaded — click Generate to try it instantly")

    st.markdown("<br>", unsafe_allow_html=True)
    col_run, col_clr = st.columns([4, 1])
    with col_run:
        run_clicked = st.button("✦  Generate SOAP Note", type="primary", use_container_width=True)
    with col_clr:
        clear_clicked = st.button("Clear", use_container_width=True)

    if clear_clicked:
        clear_sensitive_data()
        st.rerun()

    if run_clicked:
        active_audio = recorded_audio or audio_file or None
        st.session_state.session_id = new_session_id()
        loading_slot = st.empty()
        try:
            with loading_slot:
                show_loading_screen("Generating SOAP note...")
            with st.spinner("Processing consultation…"):
                tx = transcript_input if "transcript_input" in dir() else SAMPLE_TRANSCRIPT
                (st.session_state.raw_transcript, st.session_state.diarized_transcript,
                 st.session_state.soap_markdown, st.session_state.patient_summary,
                 st.session_state.soap_pdf_bytes, st.session_state.soap_dict) = run_pipeline(active_audio, tx)
            st.session_state.pipeline_ran = True
            log_event("GENERATED", {"source": "pipeline"})
            st.success(f"Note generated (Session: {st.session_state.session_id}) — navigate with the sidebar")
        except Exception as exc:
            st.error(str(exc))
        finally:
            loading_slot.empty()

    words = len(st.session_state.raw_transcript.split()) if st.session_state.raw_transcript else 0
    duration = f"{max(1, words // 150)}m" if words else "—"

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-val">{duration}</div><div class="metric-lbl">Current session</div></div>',
            unsafe_allow_html=True)
    with c2:
        session_id_display = st.session_state.session_id or "—"
        st.markdown(
            f'<div class="metric-card"><div class="metric-val" style="font-size:1rem;letter-spacing:0">{session_id_display}</div><div class="metric-lbl">Session ID (anonymous)</div></div>',
            unsafe_allow_html=True)
    with c3:
        st.markdown(
            '<div class="metric-card"><div class="metric-val">6m</div><div class="metric-lbl">Per consultation</div></div>',
            unsafe_allow_html=True)

    if st.session_state.raw_transcript:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Raw transcript**")
        st.text_area("Raw transcript", value=st.session_state.raw_transcript,
                     height=180, disabled=True, label_visibility="collapsed")

    if st.session_state.diarized_transcript:
        st.markdown("**Speaker diarization**")
        html = []
        for line in st.session_state.diarized_transcript.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            if line.upper().startswith("DOCTOR:"):
                speech = line[7:].strip()
                html.append(
                    f'<div class="sp-line">'
                    f'<span class="sp-tag doc">Dr</span>'
                    f'<span class="sp-sep">·</span>'
                    f'<span class="sp-speech">{speech}</span>'
                    f'</div>'
                )
            elif line.upper().startswith("PATIENT:"):
                speech = line[8:].strip()
                html.append(
                    f'<div class="sp-line">'
                    f'<span class="sp-tag pat">Pt</span>'
                    f'<span class="sp-sep">·</span>'
                    f'<span class="sp-speech">{speech}</span>'
                    f'</div>'
                )
            else:
                html.append(
                    f'<div class="sp-line">'
                    f'<span class="sp-speech" style="padding-left:4px">{line}</span>'
                    f'</div>'
                )
        st.markdown(
            "<div class='session-list-card' style='padding:10px 14px;'>" + "".join(html) + "</div>",
            unsafe_allow_html=True
        )

# ── PAGE 2: SOAP Note ─────────────────────────────────────────────────────────
elif page == "SOAP Note":
    page_header("📋", "SOAP Note", "AI-generated clinical documentation")

    if not st.session_state.pipeline_ran:
        empty_state("Go to Record & Transcribe to generate a note first.")
    else:
        st.markdown('<div class="warn-banner">⚠  AI-generated draft — review and verify before adding to the medical record or sharing with third parties.</div>', unsafe_allow_html=True)
        hipaa_banner("This note contains no patient name. Verify all clinical details before use.")
        st.markdown(st.session_state.soap_markdown)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.session_state.soap_pdf_bytes:
            if st.download_button("↓  Download PDF", data=st.session_state.soap_pdf_bytes,
                               file_name="soap_note.pdf", mime="application/pdf", use_container_width=True):
                log_event("DOWNLOADED")
                clear_sensitive_data()
                st.rerun()

# ── PAGE 3: Patient Summary ───────────────────────────────────────────────────
elif page == "Patient Summary":
    page_header("👤", "Patient Summary", "Plain-language visit summary for the patient")

    if not st.session_state.pipeline_ran:
        empty_state()
    else:
        hipaa_banner("Summary contains no patient name or identifiers — safe to print and hand to patient.")
        st.session_state.patient_summary = st.text_area(
            "Edit before sharing with the patient",
            value=st.session_state.patient_summary, height=220)
        st.caption("Editable — adjust tone or details before printing or messaging")

# ── PAGE 4: ICD-10 Codes ──────────────────────────────────────────────────────
elif page == "ICD-10 Codes":
    page_header("🏷", "ICD-10 Codes", "AI-suggested billing codes based on the assessment")

    if not st.session_state.pipeline_ran:
        empty_state()
    else:
        if st.button("✦  Suggest ICD-10 Codes", type="primary"):
            with st.spinner("Analysing assessment…"):
                codes = suggest_icd10_codes(st.session_state.soap_dict, OPENROUTER_API_KEY)
                st.session_state["icd10_codes"] = codes

        if "icd10_codes" in st.session_state:
            st.markdown("<br>", unsafe_allow_html=True)
            for item in st.session_state["icd10_codes"]:
                conf = item.get("confidence","low")
                st.markdown(f"""
                <div class="icd-row">
                    <span class="icd-code">{item.get('code','—')}</span>
                    <span class="icd-desc">{item.get('description','—')}</span>
                    <span class="icd-badge icd-{conf}">{conf}</span>
                </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption("AI suggestions only — verify with a certified coder before billing")

# ── PAGE 5: Follow-Up ────────────────────────────────────────────────────────
elif page == "Follow-Up":
    page_header("🔔", "Follow-Up Reminder", "Generate a friendly patient reminder message")

    if not st.session_state.pipeline_ran:
        empty_state()
    else:
        hipaa_banner("Reminder uses a generic greeting (no patient name) to prevent PHI exposure.")
        st.info("Patient name is not collected or stored. The reminder will use a generic greeting to stay HIPAA-safe.")

        if st.button("✦  Generate Reminder", type="primary"):
            with st.spinner("Generating…"):
                reminder = generate_followup_reminder(
                    st.session_state.soap_dict, OPENROUTER_API_KEY)
                st.session_state["followup_reminder"] = reminder

        if "followup_reminder" in st.session_state:
            st.markdown("<br>", unsafe_allow_html=True)
            st.text_area("Reminder — edit before sending", value=st.session_state["followup_reminder"], height=160)
            st.caption("Copy into your SMS platform or patient portal")

# ── PAGE 6: Send Document ─────────────────────────────────────────────────────
elif page == "Send Document":
    page_header("📡", "Send Document", "Transmit the SOAP note by fax or email")

    if not st.session_state.soap_pdf_bytes:
        empty_state()
    else:
        hipaa_banner("Contact details are used only for transmission, never written to audit logs, and cleared after send.")
        send_target = st.radio(
            "Send target",
            ["Organization only", "Patient only", "Both"],
            horizontal=True
        )

        c1, c2 = st.columns(2)
        with c1:
            recipient_org = st.text_input("Recipient organisation", placeholder="City Hospital / Dr. Smith's Clinic")
            fax_number    = st.text_input("Fax number", placeholder="+1XXXXXXXXXX")
        with c2:
            email_addr     = st.text_input("Email (optional)", placeholder="doctor@hospital.com")
            recipient_type = st.selectbox("Recipient type",
                ["Hospital / Specialist", "Lab", "Insurance", "Clinic"])

        if send_target in ("Patient only", "Both"):
            st.markdown("<br>", unsafe_allow_html=True)
            p1, p2 = st.columns(2)
            with p1:
                patient_email = st.text_input(
                    "Patient email (transient only)",
                    placeholder="patient@example.com",
                    key="patient_email_input",
                )
            with p2:
                patient_phone = st.text_input(
                    "Patient phone (optional, not sent here)",
                    placeholder="+1XXXXXXXXXX",
                    key="patient_phone_input",
                )
            attach_patient_pdf = st.checkbox("Attach SOAP PDF in patient email", value=False)
        else:
            patient_email = ""
            patient_phone = ""
            attach_patient_pdf = False

        st.markdown("<br>", unsafe_allow_html=True)
        method = st.radio("Transmission method", ["Mock (test)","Kno2 Fax","Email"], horizontal=True)

        needs_email_auth = method == "Email" or send_target in ("Patient only", "Both")
        if needs_email_auth:
            st.markdown("<br>", unsafe_allow_html=True)
            e1, e2 = st.columns(2)
            with e1:
                smtp_host    = st.text_input("SMTP host", value="smtp.gmail.com")
                sender_email = st.text_input("Sender email", key="sender_email_input")
            with e2:
                smtp_port       = st.number_input("SMTP port", value=465)
                sender_password = st.text_input("App password", type="password", key="sender_password_input")
        else:
            smtp_host=smtp_port=sender_email=sender_password=""

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✦  Send Document", type="primary", use_container_width=True):
            org_result = None
            patient_result = None
            with st.spinner("Transmitting…"):
                send_org     = send_target in ("Organization only", "Both")
                send_patient = send_target in ("Patient only", "Both")

                if send_org:
                    if method == "Mock (test)":
                        org_result = send_with_retry(
                            send_via_mock, retries=2,
                            pdf_bytes=st.session_state.soap_pdf_bytes,
                            recipient=recipient_org
                        )
                    elif method == "Kno2 Fax":
                        org_result = send_via_kno2(st.session_state.soap_pdf_bytes, fax_number)
                    elif method == "Email" and sender_email:
                        org_result = send_with_retry(
                            send_via_email, retries=2,
                            pdf_bytes=st.session_state.soap_pdf_bytes,
                            to_email=email_addr or sender_email,
                            smtp_host=smtp_host, smtp_port=int(smtp_port),
                            sender_email=sender_email, sender_password=sender_password,
                            provider_tag="email_org"
                        )
                    else:
                        st.warning("Please fill in all required organization fields.")

                if send_patient:
                    if not patient_email or not sender_email or not sender_password:
                        st.warning("Patient send requires patient email and sender email/app password.")
                    else:
                        reminder_text = st.session_state.get("followup_reminder", "")
                        summary_text  = st.session_state.get("patient_summary", "")
                        patient_body  = (
                            "Hello,\n\n"
                            "Here is your visit follow-up from BitDoc.\n\n"
                            f"{summary_text or 'Your visit summary is ready.'}\n\n"
                            f"{reminder_text if reminder_text else ''}\n\n"
                            "If symptoms worsen, contact your care team."
                        )
                        patient_result = send_with_retry(
                            send_via_email, retries=2,
                            pdf_bytes=st.session_state.soap_pdf_bytes if attach_patient_pdf else b"",
                            to_email=patient_email,
                            smtp_host=smtp_host, smtp_port=int(smtp_port),
                            sender_email=sender_email, sender_password=sender_password,
                            subject=f"Your Visit Summary — {datetime.date.today()}",
                            body=patient_body,
                            attach_pdf=attach_patient_pdf,
                            attachment_name=f"visit_note_{datetime.date.today()}.pdf",
                            provider_tag="email_patient"
                        )

            if org_result:
                log_event("SENT" if org_result["success"] else "FAILED",
                          {"provider": org_result.get("provider"),
                           "message_id": org_result.get("message_id"),
                           "recipient_type": recipient_type,
                           "attempts": org_result.get("attempts"),
                           "status": "success" if org_result.get("success") else "failed",
                           "error": org_result.get("error")})
                if org_result["success"]:
                    st.success(f"Organization transmission successful · ID: {org_result['message_id']}")
                else:
                    st.error(f"Organization transmission failed · {org_result.get('error','Unknown error')}")

            if patient_result:
                log_event("SENT" if patient_result["success"] else "FAILED",
                          {"provider": patient_result.get("provider"),
                           "message_id": patient_result.get("message_id"),
                           "recipient_type": "Patient",
                           "attempts": patient_result.get("attempts"),
                           "status": "success" if patient_result.get("success") else "failed",
                           "error": patient_result.get("error")})
                if patient_result["success"]:
                    st.success(f"Patient message sent · ID: {patient_result['message_id']}")
                else:
                    st.error(f"Patient message failed · {patient_result.get('error','Unknown error')}")

            clear_transient_contact_fields()

            sent_any = (org_result and org_result.get("success")) or (patient_result and patient_result.get("success"))
            if sent_any:
                clear_sensitive_data()
                st.info("Session data cleared after transmission for HIPAA compliance.")

# ── PAGE 7: Audit Log ─────────────────────────────────────────────────────────
elif page == "Audit Log":
    page_header("🗂", "Audit Log", "All actions recorded in this session")

    hipaa_banner("Audit log contains session IDs only — no patient names or PHI are ever recorded.")

    log = st.session_state.audit_log
    if not log:
        empty_state("No events logged yet.")
    else:
        action_colors = {
            "GENERATED":  "#C9A96E",
            "SENT":       "#4ADE80",
            "FAILED":     "#F87171",
            "DOWNLOADED": "#A78BFA",
            "VIEWED":     "#60A5FA",
        }

        st.markdown("""
        <div style="color:#5C5850;font-size:0.68rem;text-transform:uppercase;
             letter-spacing:0.12em;font-weight:700;border-bottom:1px solid rgba(0,0,0,0.08);
             padding-bottom:6px;display:grid;grid-template-columns:120px 100px 1fr 100px;gap:12px;margin-bottom:8px;">
            <span>Time</span><span>Action</span><span>Session ID</span><span>Provider</span>
        </div>""", unsafe_allow_html=True)

        for entry in reversed(log[-30:]):
            c = action_colors.get(entry.get("action",""), "#5C5850")
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:120px 100px 1fr 100px;gap:12px;
                        padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.04);font-size:0.82rem;">
                <span style="color:#64748B">{entry.get('timestamp','')}</span>
                <span style="color:{c};font-weight:700">{entry.get('action','')}</span>
                <span style="color:#334155;font-family:monospace">{entry.get('session_id','—')}</span>
                <span style="color:#64748B">{entry.get('provider','—')}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=AUDIT_LOG_FIELDS, extrasaction="ignore")
        w.writeheader()
        for e in log:
            row = {k: _audit_val(e.get(k, "—")) for k in AUDIT_LOG_FIELDS}
            w.writerow(row)
        st.download_button("↓  Export Audit Log CSV", data=buf.getvalue().encode(),
                           file_name=f"BitDoc_audit_{datetime.date.today()}.csv", mime="text/csv")

# ── Disclaimer ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
    <strong>Clinical Disclaimer</strong> — All AI-generated notes must be reviewed by a licensed
    clinician before clinical use. BitDoc is an AI assistant, not a substitute for clinical judgment.
    This app operates in HIPAA-safe mode: no patient names are stored, sessions auto-expire after 5 minutes,
    and all PHI-adjacent data is cleared after download or transmission.
</div>
""", unsafe_allow_html=True)