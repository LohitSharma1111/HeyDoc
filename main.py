import streamlit as st

st.set_page_config(
    page_title="BitDoc · Medical Scribe",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.write("VERSION 2 - CHECK")


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
    # FIX 2: Splash background → white; logo + "BitDoc" text → teal (#12C4B3)
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

/* Keep Streamlit header controls visually consistent */
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
/* Sidebar toggle button - avoid raw Material icon text if the font is unavailable */

/* FIX 3: Sidebar collapse button — hide ALL child text nodes that render raw icon names */
header[data-testid="stHeader"] button[kind="header"][aria-label*="sidebar" i],
header[data-testid="stHeader"] button[kind="header"][title*="sidebar" i],
section[data-testid="stSidebar"] button[kind="header"][aria-label*="sidebar" i],
section[data-testid="stSidebar"] button[kind="header"][title*="sidebar" i] {
    min-width: 2.25rem !important;
    width: 2.25rem !important;
    height: 2.25rem !important;
    padding: 0 !important;
    color: transparent !important;
    font-size: 0 !important;
    line-height: 0 !important;
    text-indent: -9999px !important;
    white-space: nowrap !important;
    position: relative !important;
    overflow: hidden !important;
}
section[data-testid="stSidebar"] button[kind="header"][aria-label*="sidebar" i],
section[data-testid="stSidebar"] button[kind="header"][title*="sidebar" i] {
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}
header[data-testid="stHeader"] button[kind="header"][aria-label*="sidebar" i] *,
header[data-testid="stHeader"] button[kind="header"][title*="sidebar" i] *,
section[data-testid="stSidebar"] button[kind="header"][aria-label*="sidebar" i] *,
section[data-testid="stSidebar"] button[kind="header"][title*="sidebar" i] * {
    font-size: 0 !important;
    line-height: 0 !important;
    color: transparent !important;
    opacity: 0 !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    display: block !important;
}
header[data-testid="stHeader"] button[kind="header"][aria-label*="sidebar" i]::before,
header[data-testid="stHeader"] button[kind="header"][title*="sidebar" i]::before,
section[data-testid="stSidebar"] button[kind="header"][aria-label*="sidebar" i]::before,
section[data-testid="stSidebar"] button[kind="header"][title*="sidebar" i]::before {
    content: "" !important;
    position: absolute !important;
    inset: 0 !important;
    margin: auto !important;
    width: 18px !important;
    height: 2px !important;
    border-radius: 999px !important;
    background: var(--sb-ink-2) !important;
    box-shadow: 0 -6px 0 var(--sb-ink-2), 0 6px 0 var(--sb-ink-2) !important;
    visibility: visible !important;
    opacity: 1 !important;
}
header[data-testid="stHeader"] button[kind="header"][aria-label*="sidebar" i]:hover::before,
header[data-testid="stHeader"] button[kind="header"][title*="sidebar" i]:hover::before,
section[data-testid="stSidebar"] button[kind="header"][aria-label*="sidebar" i]:hover::before,
section[data-testid="stSidebar"] button[kind="header"][title*="sidebar" i]:hover::before {
    background: var(--sb-ink) !important;
    box-shadow: 0 -6px 0 var(--sb-ink), 0 6px 0 var(--sb-ink) !important;
}
section[data-testid="stSidebar"] button[kind="header"],
section[data-testid="stSidebar"] button[kind="header"]:hover,
section[data-testid="stSidebar"] button[kind="header"]:focus {
    color: transparent !important;
    font-size: 0 !important;
    line-height: 0 !important;
    text-indent: -9999px !important;
    text-shadow: none !important;
}
section[data-testid="stSidebar"] button[kind="header"]::after,
section[data-testid="stSidebar"] button[kind="header"]:hover::after,
section[data-testid="stSidebar"] button[kind="header"]:focus::after {
    content: "" !important;
}
section[data-testid="stSidebar"] > div:first-child {
    color: transparent !important;
    font-size: 0 !important;
    line-height: 0 !important;
    text-shadow: none !important;
}
section[data-testid="stSidebar"] > div:first-child * {
    text-shadow: none !important;
}
section[data-testid="stSidebar"] > div:first-child button[kind="header"]::after {
    content: "" !important;
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

.stRadio > div { gap: 6px !important; }
.stRadio > div > label {
    background: transparent !important; border: 1px solid transparent !important;
    border-radius: var(--r-sm) !important; padding: 10px 14px !important;
    cursor: pointer !important; color: var(--sb-ink-2) !important;
    font-size: 0.85rem !important; font-weight: 600 !important;
    transition: all 0.2s ease !important;
    display: flex !important; align-items: center !important;
}
.stRadio > div > label:hover { background: var(--sb-surface) !important; color: var(--sb-ink) !important; }
.stRadio > div > label:has(input:checked) { background: rgba(18,196,179,0.1) !important; color: var(--teal) !important; font-weight: 700 !important; }
.stRadio > div > label > div:first-child { display: none !important; }

.nav-section-label { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.16em; color: var(--sb-ink-3); padding: 16px 14px 8px; font-weight: 800; }

.status-pill { display: flex; align-items: center; gap: 8px; padding: 9px 12px; border-radius: 8px; font-size: 0.72rem; font-weight: 700; border: 1px solid; margin: 8px 6px 0; text-transform: uppercase; letter-spacing: 0.06em; }
.status-pill.ready { background: rgba(16,185,129,0.08); border-color: rgba(16,185,129,0.3); color: #10B981; }
.status-pill.empty { background: rgba(255,255,255,0.02); border-color: var(--sb-border); color: var(--sb-ink-3); }
.status-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.status-dot.ready { background: #10B981; box-shadow: 0 0 8px #10B981; animation: livepulse 2s infinite; }
.status-dot.empty { background: var(--sb-ink-3); }

/* HIPAA badge */
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

.metric-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r); padding: 18px 16px; text-align: left; transition: border-color 0.2s ease; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
.metric-card:hover { border-color: var(--border-hi); }
.metric-val { font-size: 2rem; font-weight: 800; color: var(--ink); letter-spacing: -0.04em; margin: 8px 0 2px; }
.metric-lbl { font-size: 0.72rem; color: var(--ink-3); text-transform: uppercase; font-weight: 800; letter-spacing: 0.1em; }

.stTextArea textarea, .stTextInput input, .stSelectbox select { background: var(--surface) !important; border: 1px solid var(--border-hi) !important; border-radius: 9px !important; color: var(--ink) !important; font-size: 0.88rem !important; transition: border-color 0.2s ease !important; padding: 12px 14px !important; box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important; }
.stTextArea textarea:focus, .stTextInput input:focus { border-color: var(--teal) !important; box-shadow: 0 0 0 3px rgba(18,196,179,0.12) !important; outline: none !important; }
.stTextArea textarea:disabled { color: #000000 !important; -webkit-text-fill-color: #000000 !important; opacity: 1 !important; }
label, .stSelectbox label { color: var(--ink-3) !important; font-size: 0.7rem !important; font-weight: 800 !important; text-transform: uppercase !important; letter-spacing: 0.14em !important; margin-bottom: 6px !important; }

.session-list-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r); margin-top: 14px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }

/* FIX 1: Diarization speaker tags — Doctor = teal, Patient = blue; clear separator */
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
    # FIX 1: Clarified prompt — first speaker (asking questions) = DOCTOR, responding speaker = PATIENT
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

def create_soap_pdf_bytes(soap):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether

    s,o,a,p = soap.get("subjective",{}),soap.get("objective",{}),soap.get("assessment",{}),soap.get("plan",{})
    def val(x): return str(x).strip() if x not in (None,"",[]) else "Not documented"
    def bul(items):
        if not items: return [("• Not documented",)]
        return [(f"• {str(i).strip()}",) for i in items if str(i).strip()]

    DARK = colors.HexColor("#0C0D0F"); PANEL = colors.HexColor("#18191C")
    GOLD = colors.HexColor("#C9A96E"); GOLD_DIM = colors.HexColor("#8A6E3E")
    INK  = colors.HexColor("#F0EDE8"); INK2 = colors.HexColor("#A09A91")
    BORDER = colors.HexColor("#2A2B2E"); WHITE = colors.white
    GREEN = colors.HexColor("#059669"); BLUE = colors.HexColor("#1D4ED8")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
        leftMargin=0.75*inch, rightMargin=0.75*inch,
        topMargin=0.6*inch, bottomMargin=0.7*inch,
        title="SOAP Note — BitDoc")
    base = getSampleStyleSheet()
    def ps(name, **kw): return ParagraphStyle(name, parent=base["Normal"], **kw)

    s_ht  = ps("HT", fontSize=20,leading=24,textColor=INK,fontName="Helvetica-Bold",alignment=TA_CENTER)
    s_sub = ps("SB", fontSize=8, leading=12,textColor=INK2,fontName="Helvetica",alignment=TA_CENTER)
    s_sh  = ps("SH", fontSize=9, leading=13,textColor=WHITE,fontName="Helvetica-Bold")
    s_lbl = ps("LB", fontSize=7, leading=10,textColor=GOLD,fontName="Helvetica-Bold",spaceBefore=6,spaceAfter=1)
    s_bod = ps("BD", fontSize=9, leading=14,textColor=INK2,fontName="Helvetica",spaceAfter=3)
    s_bul = ps("BU", fontSize=9, leading=14,textColor=INK2,fontName="Helvetica",leftIndent=8,spaceAfter=2)
    s_wrn = ps("WN", fontSize=7.5,leading=11,textColor=colors.HexColor("#D4A017"),fontName="Helvetica-Oblique")
    s_ftr = ps("FT", fontSize=7, leading=10,textColor=INK2,fontName="Helvetica",alignment=TA_CENTER)

    today = datetime.date.today().strftime("%B %d, %Y")

    def sec(badge, title, accent=DARK):
        b = Paragraph(f"<b>{badge}</b>", ParagraphStyle("bx",fontSize=11,textColor=GOLD,fontName="Helvetica-Bold",alignment=TA_CENTER))
        h = Paragraph(title, s_sh)
        t = Table([[b,h]], colWidths=[0.38*inch,None])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),accent),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(0,0),7),("RIGHTPADDING",(0,0),(0,0),5),
            ("LEFTPADDING",(1,0),(1,0),10),
            ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("ROUNDEDCORNERS",[5]),("LINEBELOW",(0,0),(-1,-1),0.5,GOLD_DIM),
        ]))
        return t

    def card(*elems):
        rows = [[e] for e in elems]
        t = Table(rows, colWidths=[doc.width])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),PANEL),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
            ("ROUNDEDCORNERS",[5]),("BOX",(0,0),(-1,-1),0.5,BORDER),
        ]))
        return t

    def bcard(items):
        return card(*[Paragraph(t, s_bul) for (t,) in bul(items)])

    def rule(): return HRFlowable(width="100%",thickness=0.5,color=BORDER,spaceAfter=8,spaceBefore=5)

    story = []
    h = Table([[Paragraph("SOAP NOTE",s_ht)],[Paragraph("BitDoc · AI Medical Scribe",s_sub)],[Paragraph(today,s_sub)]],colWidths=[doc.width])
    h.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),DARK),("TOPPADDING",(0,0),(-1,-1),10),
        ("BOTTOMPADDING",(0,0),(-1,-1),10),("LEFTPADDING",(0,0),(-1,-1),16),("ROUNDEDCORNERS",[7]),
        ("BOX",(0,0),(-1,-1),1,colors.HexColor("#2A2B2E"))]))
    story += [h, Spacer(1,8)]

    wt = Table([[Paragraph("⚠  AI draft — verify before clinical use or sharing",s_wrn)]],colWidths=[doc.width])
    wt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#1A1500")),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),12),("ROUNDEDCORNERS",[4]),
        ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#4A3800"))]))
    story += [wt, Spacer(1,14)]

    sval = soap.get("subjective",{})
    oval = soap.get("objective",{})
    aval = soap.get("assessment",{})
    pval = soap.get("plan",{})

    story += [KeepTogether([sec("S","SUBJECTIVE"),Spacer(1,6),
        card(Paragraph("Chief Complaint",s_lbl),Paragraph(val(sval.get("chief_complaint")),s_bod),
             Paragraph("History of Present Illness",s_lbl),Paragraph(val(sval.get("history_of_present_illness")),s_bod)),Spacer(1,6)]),
        Paragraph("Symptoms",s_lbl), bcard(sval.get("symptoms",[])), Spacer(1,12), rule()]

    story += [KeepTogether([sec("O","OBJECTIVE"),Spacer(1,6),
        card(Paragraph("Vitals",s_lbl),Paragraph(val(oval.get("vitals")),s_bod),
             Paragraph("Physical Examination",s_lbl),Paragraph(val(oval.get("physical_exam")),s_bod)),Spacer(1,6)]),
        Paragraph("Clinical Observations",s_lbl), bcard(oval.get("observations",[])), Spacer(1,12), rule()]

    story += [KeepTogether([sec("A","ASSESSMENT",colors.HexColor("#0F1A0E")),Spacer(1,6),
        card(Paragraph("Primary Diagnosis",s_lbl),Paragraph(val(aval.get("diagnosis")),s_bod)),Spacer(1,6)]),
        Paragraph("Differential Diagnoses",s_lbl), bcard(aval.get("differential",[])), Spacer(1,12), rule()]

    story += [sec("P","PLAN",colors.HexColor("#0E0F1A")), Spacer(1,6),
        Paragraph("Investigations / Orders",s_lbl), bcard(pval.get("investigations",[])), Spacer(1,5),
        Paragraph("Medications",s_lbl), bcard(pval.get("medications",[])), Spacer(1,5),
        card(Paragraph("Follow-Up",s_lbl),Paragraph(val(pval.get("follow_up")),s_bod),
             Paragraph("Patient Instructions",s_lbl),Paragraph(val(pval.get("instructions")),s_bod)),
        Spacer(1,20), rule(),
        Paragraph(f"BitDoc AI Medical Scribe  ·  {today}  ·  All AI-generated notes must be reviewed by a licensed clinician before clinical use",s_ftr)]

    doc.build(story)
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

def log_event(action, details=None):
    session_id = st.session_state.get("session_id", "UNKNOWN")
    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "action": action,
        "session_id": session_id,
        "patient": "anonymous",
        **(details or {}),
    }
    st.session_state.audit_log.append(entry)

def send_via_mock(pdf_bytes, recipient):
    time.sleep(0.5)
    ok = random.random() > 0.2
    return {"success":ok,"message_id":f"MOCK-{random.randint(10000,99999)}","provider":"mock",
            "error":None if ok else "Simulated failure"}

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

def send_via_email(pdf_bytes, to_email, smtp_host, smtp_port, sender_email, sender_password):
    try:
        msg = EmailMessage()
        msg["Subject"] = f"SOAP Note — {datetime.date.today()}"
        msg["From"] = sender_email; msg["To"] = to_email
        msg.set_content(f"SOAP note attached.\nGenerated by BitDoc AI Medical Scribe. Review before clinical use.")
        msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf",
                           filename=f"soap_{datetime.date.today()}.pdf")
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as smtp:
            smtp.login(sender_email, sender_password); smtp.send_message(msg)
        return {"success":True,"message_id":f"EMAIL-{random.randint(10000,99999)}","provider":"email","error":None}
    except Exception as e:
        return {"success":False,"message_id":None,"provider":"email","error":str(e)}

def send_with_retry(send_fn, retries=2, delay=1.0, **kwargs):
    last = {}
    for i in range(1, retries+1):
        r = send_fn(**kwargs)
        if r["success"]: r["attempts"]=i; return r
        last = r
        if i < retries: time.sleep(delay)
    last["attempts"] = retries; return last

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
        try:
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

    # FIX 1: Diarization display — proper tag styling + "·" separator between role and text
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
        hipaa_banner("Recipient details are used for transmission only and not stored in this session.")
        c1, c2 = st.columns(2)
        with c1:
            recipient_org = st.text_input("Recipient organisation", placeholder="City Hospital / Dr. Smith's Clinic")
            fax_number    = st.text_input("Fax number", placeholder="+1XXXXXXXXXX")
        with c2:
            email_addr     = st.text_input("Email (optional)", placeholder="doctor@hospital.com")
            recipient_type = st.selectbox("Recipient type",
                ["Hospital / Specialist", "Lab", "Insurance", "Clinic"])

        st.markdown("<br>", unsafe_allow_html=True)
        method = st.radio("Transmission method", ["Mock (test)","Kno2 Fax","Email"], horizontal=True)

        if method == "Email":
            st.markdown("<br>", unsafe_allow_html=True)
            e1, e2 = st.columns(2)
            with e1:
                smtp_host    = st.text_input("SMTP host", value="smtp.gmail.com")
                sender_email = st.text_input("Sender email")
            with e2:
                smtp_port       = st.number_input("SMTP port", value=465)
                sender_password = st.text_input("App password", type="password")
        else:
            smtp_host=smtp_port=sender_email=sender_password=""

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✦  Send Document", type="primary", use_container_width=True):
            with st.spinner("Transmitting…"):
                if method == "Mock (test)":
                    result = send_with_retry(send_via_mock, retries=2,
                                             pdf_bytes=st.session_state.soap_pdf_bytes,
                                             recipient=recipient_org)
                elif method == "Kno2 Fax":
                    result = send_via_kno2(st.session_state.soap_pdf_bytes, fax_number)
                elif method == "Email" and sender_email:
                    result = send_with_retry(send_via_email, retries=2,
                                             pdf_bytes=st.session_state.soap_pdf_bytes,
                                             to_email=email_addr or sender_email,
                                             smtp_host=smtp_host, smtp_port=int(smtp_port),
                                             sender_email=sender_email,
                                             sender_password=sender_password)
                else:
                    st.warning("Please fill in all required fields."); result = None

            if result:
                log_event("SENT" if result["success"] else "FAILED",
                          {"provider": result.get("provider"),
                           "message_id": result.get("message_id"),
                           "recipient_type": recipient_type})
                if result["success"]:
                    st.success(f"Transmitted successfully · ID: {result['message_id']}")
                    clear_sensitive_data()
                    st.info("Session data cleared after transmission for HIPAA compliance.")
                else:
                    st.error(f"Transmission failed · {result.get('error','Unknown error')}")

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
        all_keys = set()
        for e in log: all_keys.update(e.keys())
        w = csv.DictWriter(buf, fieldnames=list(all_keys))
        w.writeheader()
        [w.writerow(e) for e in log]
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
