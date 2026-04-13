import streamlit as st

st.set_page_config(
    page_title="HeyDoc · Medical Scribe",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


if "splash_shown" not in st.session_state:
    st.session_state.splash_shown = True
    st.markdown('''
    <style>
    .splash-screen {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: radial-gradient(circle at center, #15171A 0%, #08090A 100%);
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
        filter: drop-shadow(0 10px 25px rgba(212, 175, 55, 0.4));
    }
    .splash-text {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 3.5rem;
        color: #D4AF37;
        opacity: 0;
        letter-spacing: 0.05em;
        font-weight: 500;
        text-shadow: 0 4px 20px rgba(212, 175, 55, 0.3);
        animation: fadeInText 1.2s ease-out forwards;
        animation-delay: 0.8s;
    }
    .splash-sub {
        font-family: 'Inter', sans-serif;
        color: #8E8A83;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.3em;
        margin-top: 15px;
        opacity: 0;
        animation: fadeInText 1s ease-out forwards;
        animation-delay: 1.2s;
    }
    
    @keyframes fadeOutSplash {
        0% { opacity: 1; pointer-events: all; backdrop-filter: blur(10px); }
        99% { opacity: 0; pointer-events: none; backdrop-filter: blur(0px); }
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
        50% { transform: translateY(-10px); filter: drop-shadow(0 15px 35px rgba(212, 175, 55, 0.6)); }
        100% { transform: translateY(0); }
    }
    
    /* Hide scrollbar during splash */
    body:has(.splash-screen) {
        overflow: hidden !important;
    }
    
    </style>
    <div class="splash-screen">
        <div class="splash-logo">🩺</div>
        <div class="splash-text">HeyDoc</div>
        <div class="splash-sub">Medical Scribe</div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Inter:wght@300;400;500;600&family=Fira+Code:wght@400;500&display=swap');

:root {
    --bg:       #08090A;
    --surface:  #0F1113;
    --panel:    #15171A;
    --lift:     #1C1E22;
    --border:   rgba(212, 175, 55, 0.15);
    --border-hi: rgba(212, 175, 55, 0.35);
    --gold:     #D4AF37;
    --gold-dim: #99812A;
    --gold-glow:rgba(212, 175, 55, 0.25);
    --ink:      #FDFBF7;
    --ink-2:    #D1CDC5;
    --ink-3:    #8E8A83;
    --green:    #4ADE80;
    --red:      #F87171;
    --blue:     #60A5FA;
    --r:        16px;
    --r-sm:     10px;
}

/* ── Reset & base ─────────────────────────────────────────── */
*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    -webkit-font-smoothing: antialiased !important;
    letter-spacing: 0.02em !important;
}

/* Restore icon fonts */
.material-icons, 
.material-symbols-rounded, 
.material-symbols-outlined, 
[class*="icon"], 
[class*="stIcon"],
[data-testid*="Icon"] {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
    letter-spacing: normal !important;
}

.stApp {
    background: var(--bg) !important;
    min-height: 100vh;
}

/* subtle noise grain overlay for premium texture */
.stApp::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.035'/%3E%3C/svg%3E");
    opacity: 0.5;
}

/* ── Sidebar ──────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    width: 240px !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.2rem !important;
}
section[data-testid="stSidebar"] > div { background: transparent !important; }

/* brand block */
.brand-block {
    display: flex; align-items: center; gap: 14px;
    padding: 18px 14px 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 20px;
}
.brand-icon {
    width: 42px; height: 42px; border-radius: 12px;
    background: linear-gradient(135deg, #D4AF37 0%, #99812A 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    box-shadow: 0 6px 20px rgba(212, 175, 55, 0.35);
    flex-shrink: 0;
    transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.4s ease;
}
.brand-block:hover .brand-icon {
    transform: scale(1.1) rotate(5deg);
    box-shadow: 0 8px 25px rgba(212, 175, 55, 0.5);
}
.brand-name {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-size: 1.4rem; color: var(--ink); letter-spacing: 0.02em;
    line-height: 1.1;
    font-weight: 600;
}
.brand-sub {
    font-size: 0.65rem; color: var(--gold-dim); text-transform: uppercase;
    letter-spacing: 0.2em; font-weight: 600; margin-top: 4px;
}

/* nav items */
.stRadio > div { gap: 6px !important; }
.stRadio > div > label {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: var(--r-sm) !important;
    padding: 12px 14px !important;
    cursor: pointer !important;
    color: var(--ink-2) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    transition: all 0.3s cubic-bezier(.4,0,.2,1) !important;
    letter-spacing: 0.02em !important;
    text-transform: none !important;
    margin-bottom: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
.stRadio > div > label * { color: inherit !important; transition: all 0.3s ease !important; }
.stRadio > div > label:hover {
    background: var(--lift) !important;
    color: var(--ink) !important;
    border-color: rgba(212, 175, 55, 0.15) !important;
    transform: translateX(4px) !important;
}
.stRadio > div > label:has(input:checked) {
    background: linear-gradient(135deg, rgba(212, 175, 55, 0.15), rgba(212, 175, 55, 0.05)) !important;
    color: var(--gold) !important;
    border-color: rgba(212, 175, 55, 0.4) !important;
    font-weight: 500 !important;
    transform: translateX(6px) !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
}
.stRadio > div > label:has(input:checked) * { color: var(--gold) !important; }
.stRadio > div > label > div:first-child { display: none !important; }

/* status pill */
.status-pill {
    display: flex; align-items: center; gap: 8px;
    padding: 10px 14px; border-radius: var(--r-sm);
    font-size: 0.76rem; font-weight: 600;
    border: 1px solid;
    margin-top: 8px;
    transition: all 0.4s ease;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.status-pill.ready {
    background: rgba(74,222,128,0.08);
    border-color: rgba(74,222,128,0.3);
    color: #4ADE80;
    box-shadow: 0 4px 15px rgba(74,222,128,0.1);
}
.status-pill.empty {
    background: rgba(255,255,255,0.02);
    border-color: var(--border);
    color: var(--ink-3);
}
.status-dot {
    width: 6px; height: 6px; border-radius: 50%;
    flex-shrink: 0;
    transition: box-shadow 0.4s ease;
}
.status-dot.ready { background: #4ADE80; box-shadow: 0 0 10px #4ADE80; animation: pulse 2s infinite; }
.status-dot.empty { background: var(--ink-3); }

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(74,222,128,0.4); }
    70% { box-shadow: 0 0 0 6px rgba(74,222,128,0); }
    100% { box-shadow: 0 0 0 0 rgba(74,222,128,0); }
}

/* divider label in sidebar */
.nav-section-label {
    font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.2em;
    color: var(--ink-3); padding: 16px 14px 8px;
    font-weight: 600;
}

/* ── Main content ─────────────────────────────────────────── */
.block-container { padding: 2.5rem 3rem 4rem !important; }

/* ── Page header ──────────────────────────────────────────── */
.ph-wrap {
    display: flex; align-items: flex-start; gap: 20px;
    margin-bottom: 2.5rem; padding-bottom: 1.8rem;
    border-bottom: 1px solid var(--border);
    transition: transform 0.3s ease;
}
.ph-wrap:hover .ph-icon-wrap {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 8px 25px rgba(212, 175, 55, 0.25);
}
.ph-icon-wrap {
    width: 52px; height: 52px; border-radius: 14px;
    background: linear-gradient(135deg, rgba(212, 175, 55, 0.25), rgba(212, 175, 55, 0.08));
    border: 1px solid rgba(212, 175, 55, 0.4);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; flex-shrink: 0; margin-top: 2px;
    box-shadow: 0 6px 20px rgba(212, 175, 55, 0.15);
    transition: all 0.4s ease;
}
.ph-title {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-size: 2.2rem; color: var(--ink); letter-spacing: -0.01em;
    line-height: 1.15; margin: 0; font-weight: 500;
}
.ph-sub {
    font-size: 0.9rem; color: var(--ink-2); margin: 6px 0 0;
    font-weight: 300; letter-spacing: 0.02em;
    font-style: italic;
}

/* ── Cards / Panels ───────────────────────────────────────── */
.panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 28px 28px;
    margin-bottom: 18px;
    position: relative; overflow: hidden;
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.panel::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.4), transparent);
    opacity: 0.5;
    transition: opacity 0.4s ease;
}
.panel:hover {
    border-color: var(--border-hi);
    box-shadow: 0 12px 35px rgba(0,0,0,0.4), 0 0 20px rgba(212, 175, 55, 0.1);
    transform: translateY(-4px);
}
.panel:hover::before { opacity: 1; }

/* ── Buttons ──────────────────────────────────────────────── */
.stButton > button {
    border-radius: var(--r-sm) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 12px 24px !important;
    background: var(--lift) !important;
    color: var(--ink-2) !important;
    border: 1px solid var(--border-hi) !important;
    transition: all 0.3s cubic-bezier(.4,0,.2,1) !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
}
.stButton > button:hover {
    background: #23262A !important;
    color: var(--ink) !important;
    border-color: rgba(212, 175, 55, 0.6) !important;
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #D4AF37 0%, #AA7C11 100%) !important;
    color: #08090A !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    font-weight: 600 !important;
    box-shadow: 0 6px 20px rgba(212, 175, 55, 0.3) !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    font-size: 0.85rem !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #F0C95A 0%, #C9991C 100%) !important;
    box-shadow: 0 12px 30px rgba(212, 175, 55, 0.5) !important;
    transform: translateY(-3px) scale(1.02) !important;
    color: #08090A !important;
}
.stButton > button[kind="primary"]:active {
    transform: translateY(1px) !important;
    box-shadow: 0 4px 10px rgba(212, 175, 55, 0.3) !important;
}

/* ── Inputs ───────────────────────────────────────────────── */
.stTextArea textarea, .stTextInput input, .stSelectbox select {
    background: var(--panel) !important;
    border: 1px solid var(--border-hi) !important;
    border-radius: var(--r) !important;
    color: var(--ink) !important;
    font-size: 0.9rem !important;
    font-family: 'Inter', sans-serif !important;
    caret-color: var(--gold) !important;
    transition: all 0.3s ease !important;
    padding: 14px 16px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 4px rgba(212, 175, 55, 0.15) !important;
    outline: none !important;
    background: var(--surface) !important;
    transform: translateY(-1px) !important;
}
label, .stSelectbox label {
    color: var(--ink-3) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    margin-bottom: 8px !important;
}
.stTextArea textarea::placeholder, .stTextInput input::placeholder {
    color: var(--ink-3) !important;
    opacity: 0.6 !important;
    font-weight: 300 !important;
}

/* ── Tabs ─────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 12px !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--ink-3) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 12px 24px !important;
    letter-spacing: 0.03em !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.3s ease !important;
    background: transparent !important;
    border-radius: 6px 6px 0 0 !important;
}
.stTabs [data-baseweb="tab"]:hover { 
    color: var(--ink) !important; 
    background: rgba(255,255,255,0.02) !important;
}
.stTabs [aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom-color: var(--gold) !important;
    background: linear-gradient(180deg, transparent, rgba(212, 175, 55, 0.05)) !important;
    text-shadow: 0 0 15px rgba(212, 175, 55, 0.3) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    border: none !important;
    padding: 24px 0 0 !important;
}

/* ── Alerts ───────────────────────────────────────────────── */
.stSuccess {
    background: rgba(74,222,128,0.08) !important;
    border: 1px solid rgba(74,222,128,0.25) !important;
    border-radius: var(--r-sm) !important;
    color: #4ADE80 !important;
    box-shadow: 0 4px 15px rgba(74,222,128,0.1) !important;
}
.stError {
    background: rgba(248,113,113,0.08) !important;
    border: 1px solid rgba(248,113,113,0.25) !important;
    border-radius: var(--r-sm) !important;
    color: #F87171 !important;
    box-shadow: 0 4px 15px rgba(248,113,113,0.1) !important;
}
.stInfo {
    background: rgba(96,165,250,0.08) !important;
    border: 1px solid rgba(96,165,250,0.25) !important;
    border-radius: var(--r-sm) !important;
    color: #93C5FD !important;
    box-shadow: 0 4px 15px rgba(96,165,250,0.1) !important;
}
.stWarning {
    background: rgba(251,191,36,0.08) !important;
    border: 1px solid rgba(251,191,36,0.25) !important;
    border-radius: var(--r-sm) !important;
    color: #FCD34D !important;
    box-shadow: 0 4px 15px rgba(251,191,36,0.1) !important;
}

/* ── Metric chips ─────────────────────────────────────────── */
.metric-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 24px 20px;
    text-align: center;
    position: relative; overflow: hidden;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.metric-card::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
    opacity: 0;
    transition: opacity 0.4s ease;
}
.metric-card:hover { 
    border-color: var(--border-hi); 
    transform: translateY(-5px) scale(1.02); 
    box-shadow: 0 12px 30px rgba(0,0,0,0.3), 0 0 20px rgba(212, 175, 55, 0.15);
}
.metric-card:hover::after { opacity: 1; }
.metric-val {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-size: 2.8rem; color: var(--gold); letter-spacing: -0.02em; line-height: 1;
    font-weight: 500;
    text-shadow: 0 4px 15px rgba(212, 175, 55, 0.2);
}
.metric-lbl {
    font-size: 0.7rem; color: var(--ink-2); text-transform: uppercase;
    letter-spacing: 0.15em; margin-top: 12px; font-weight: 600;
}

/* ── ICD chips ────────────────────────────────────────────── */
.icd-row {
    display: flex; align-items: center; gap: 16px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--r-sm);
    padding: 16px 20px; margin-bottom: 12px;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.icd-row:hover {
    border-color: rgba(212, 175, 55, 0.4);
    transform: translateX(6px) scale(1.01);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3), -4px 0 0 var(--gold);
    background: var(--lift);
}
.icd-code {
    font-family: 'Fira Code', monospace !important;
    font-size: 0.9rem; color: var(--gold); min-width: 70px; font-weight: 500;
}
.icd-desc { font-size: 0.9rem; color: var(--ink); flex: 1; font-weight: 400; }
.icd-badge {
    font-size: 0.7rem; padding: 4px 12px; border-radius: 20px;
    font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.icd-high   { background: rgba(74,222,128,0.12);  color: #4ADE80; border: 1px solid rgba(74,222,128,0.3); }
.icd-medium { background: rgba(251,191,36,0.12);  color: #FCD34D; border: 1px solid rgba(251,191,36,0.3); }
.icd-low    { background: rgba(248,113,113,0.12); color: #F87171; border: 1px solid rgba(248,113,113,0.3); }

/* ── Speaker diarization ──────────────────────────────────── */
.sp-line { display: flex; gap: 16px; margin: 10px 0; align-items: baseline; transition: background 0.2s ease; padding: 8px; border-radius: 8px; }
.sp-line:hover { background: rgba(255,255,255,0.02); }
.sp-tag {
    font-family: 'Fira Code', monospace !important;
    font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.12em; min-width: 65px; padding-top: 2px;
    flex-shrink: 0;
}
.sp-tag.doc { color: var(--gold); text-shadow: 0 0 10px rgba(212, 175, 55, 0.4); }
.sp-tag.pat { color: #60A5FA; text-shadow: 0 0 10px rgba(96, 165, 250, 0.4); }
.sp-speech { font-size: 0.9rem; color: var(--ink-2); line-height: 1.6; }

/* ── File uploader ────────────────────────────────────────── */
.stFileUploader > div {
    background: var(--panel) !important;
    border: 2px dashed rgba(212, 175, 55, 0.3) !important;
    border-radius: var(--r) !important;
    transition: all 0.3s ease !important;
    padding: 20px !important;
}
.stFileUploader > div:hover { 
    border-color: rgba(212, 175, 55, 0.7) !important; 
    background: rgba(212, 175, 55, 0.05) !important;
    transform: scale(1.01) !important;
}
.stFileUploader label { text-transform: none !important; letter-spacing: 0 !important; font-size: 1.1rem !important; font-weight: 500 !important; color: var(--ink) !important; }

/* ── Download button ──────────────────────────────────────── */
.stDownloadButton > button {
    background: var(--lift) !important;
    color: var(--ink) !important;
    border: 1px solid var(--border-hi) !important;
    border-radius: var(--r) !important;
    width: 100% !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding: 14px !important;
    transition: all 0.3s cubic-bezier(.4,0,.2,1) !important;
    letter-spacing: 0.03em !important;
}
.stDownloadButton > button:hover {
    background: #23262A !important;
    border-color: rgba(212, 175, 55, 0.5) !important;
    color: var(--gold) !important;
    transform: translateY(-3px) scale(1.01) !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.3) !important;
}

/* ── Expander ─────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    color: var(--ink) !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    padding: 14px 18px !important;
}
.streamlit-expanderHeader:hover {
    border-color: var(--gold) !important;
    color: var(--gold) !important;
    background: var(--lift) !important;
}
.streamlit-expanderContent {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--r-sm) var(--r-sm) !important;
    padding: 20px !important;
}

/* ── Selectbox ────────────────────────────────────────────── */
.stSelectbox [data-baseweb="select"] > div {
    background: var(--panel) !important;
    border-color: var(--border-hi) !important;
    border-radius: var(--r-sm) !important;
    color: var(--ink) !important;
    transition: all 0.3s ease !important;
}
.stSelectbox [data-baseweb="select"] > div:hover {
    border-color: rgba(212, 175, 55, 0.5) !important;
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.1) !important;
}
.stSelectbox [data-baseweb="select"] span { color: var(--ink) !important; }
.stSelectbox svg { fill: var(--gold) !important; }

/* ── Spinner ──────────────────────────────────────────────── */
.stSpinner > div { color: var(--gold) !important; }

/* ── HR ───────────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid rgba(212, 175, 55, 0.2) !important;
    margin: 24px 0 !important;
}

/* ── Markdown ─────────────────────────────────────────────── */
.stMarkdown h2 {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-size: 1.4rem !important;
    color: var(--ink) !important;
    letter-spacing: 0.01em !important;
    margin-top: 1.8em !important;
    font-weight: 600 !important;
    font-style: italic;
}
.stMarkdown h3 { color: var(--gold) !important; font-size: 0.85rem !important; text-transform: uppercase !important; letter-spacing: 0.15em !important; font-style: normal !important; font-weight: 600 !important; }
.stMarkdown p, .stMarkdown li { color: var(--ink-2) !important; font-size: 0.9rem !important; line-height: 1.8 !important; }
.stMarkdown strong { color: var(--ink) !important; font-weight: 600 !important; }
.stMarkdown hr { border-color: rgba(212, 175, 55, 0.2) !important; }
.stMarkdown ul li::marker { color: var(--gold) !important; }

/* ── Number input ─────────────────────────────────────────── */
.stNumberInput input {
    background: var(--panel) !important;
    border: 1px solid var(--border-hi) !important;
    border-radius: var(--r-sm) !important;
    color: var(--ink) !important;
    transition: all 0.3s ease !important;
}
.stNumberInput input:focus {
    border-color: var(--gold) !important;
}

/* ── Caption ──────────────────────────────────────────────── */
.stCaption, small { color: var(--ink-3) !important; font-size: 0.78rem !important; letter-spacing: 0.02em !important; }

/* ── Audio input ──────────────────────────────────────────── */
.stAudioInput { background: var(--panel) !important; border-radius: var(--r) !important; border: 1px solid var(--border-hi) !important; padding: 10px !important; }

/* ── Audit table ──────────────────────────────────────────── */
.audit-grid {
    display: grid;
    grid-template-columns: 130px 110px 1fr 110px;
    gap: 12px; align-items: center;
    padding: 12px 10px;
    border-bottom: 1px solid var(--border);
    font-size: 0.85rem;
    transition: all 0.3s ease;
}
.audit-grid:hover { background: rgba(255,255,255,0.03); border-radius: 8px; transform: scale(1.01); padding-left: 14px; }
.audit-ts { font-family: 'Fira Code', monospace !important; color: var(--ink-3); font-size: 0.78rem; }
.audit-pat { color: var(--ink); font-weight: 500; }
.audit-prv { color: var(--ink-3); font-family: 'Fira Code', monospace !important; font-size: 0.75rem; }

/* ── Disclaimer ───────────────────────────────────────────── */
.disclaimer {
    background: rgba(212, 175, 55, 0.04);
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-radius: var(--r-sm);
    padding: 16px 20px;
    font-size: 0.82rem;
    color: var(--ink-2);
    margin-top: 36px;
    line-height: 1.7;
    transition: all 0.3s ease;
}
.disclaimer:hover { border-color: rgba(212, 175, 55, 0.4); background: rgba(212, 175, 55, 0.08); }
.disclaimer strong { color: var(--gold); text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.75rem; }

/* ── Info empty state ─────────────────────────────────────── */
.empty-state {
    background: var(--panel);
    border: 1px dashed rgba(212, 175, 55, 0.3);
    border-radius: var(--r);
    padding: 48px 32px;
    text-align: center;
    color: var(--ink-3);
    font-size: 0.95rem;
    transition: all 0.3s ease;
}
.empty-state:hover {
    border-color: rgba(212, 175, 55, 0.6);
    background: var(--lift);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
.empty-state-icon { font-size: 2.5rem; margin-bottom: 16px; color: var(--gold); opacity: 0.7; animation: float 3s ease-in-out infinite; }

@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}

/* ── Warn banner ──────────────────────────────────────────── */
.warn-banner {
    background: rgba(251,191,36,0.08);
    border: 1px solid rgba(251,191,36,0.25);
    border-radius: var(--r-sm);
    padding: 12px 20px;
    font-size: 0.85rem;
    color: #FCD34D;
    margin-bottom: 24px;
    line-height: 1.6;
    box-shadow: 0 4px 15px rgba(251,191,36,0.1);
    animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ── Columns gap fix ──────────────────────────────────────── */
[data-testid="stHorizontalBlock"] { gap: 16px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
defaults = {
    "raw_transcript": "", "diarized_transcript": "", "soap_markdown": "",
    "patient_summary": "", "soap_pdf_bytes": b"", "soap_dict": {},
    "pipeline_ran": False, "audit_log": [], "patient_sessions": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand-block">
        <div class="brand-icon">🩺</div>
        <div>
            <div class="brand-name">HeyDoc</div>
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
        "Sessions",
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

# ── Imports & backend ─────────────────────────────────────────────────────────
import base64, csv, datetime, io, json, os, random, smtplib, tempfile, time
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
    prompt = f"""You are a medical conversation analyst. Label each line as DOCTOR or PATIENT.
Return ONLY:\nDOCTOR: <text>\nPATIENT: <text>\n\nRaw transcript:\n{transcript}"""
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
        title="SOAP Note — HeyDoc")
    base = getSampleStyleSheet()
    def ps(name, **kw): return ParagraphStyle(name, parent=base["Normal"], **kw)

    s_ht  = ps("HT", fontSize=20,leading=24,textColor=INK,fontName="Helvetica-Bold",alignment=TA_CENTER)
    s_sub = ps("SB", fontSize=8, leading=12,textColor=INK2,fontName="Helvetica",alignment=TA_CENTER)
    s_sh  = ps("SH", fontSize=9, leading=13,textColor=WHITE,fontName="Helvetica-Bold")
    s_lbl = ps("LB", fontSize=7, leading=10,textColor=GOLD,fontName="Helvetica-Bold",spaceBefore=6,spaceAfter=1,
               textTransform="uppercase")
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
            ("BACKGROUND",(0,0),(-1,-1),accent),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LEFTPADDING",(0,0),(0,0),7),("RIGHTPADDING",(0,0),(0,0),5),
            ("LEFTPADDING",(1,0),(1,0),10),
            ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("ROUNDEDCORNERS",[5]),
            ("LINEBELOW",(0,0),(-1,-1),0.5,GOLD_DIM),
        ]))
        return t

    def card(*elems):
        rows = [[e] for e in elems]
        t = Table(rows, colWidths=[doc.width])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),PANEL),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
            ("ROUNDEDCORNERS",[5]),
            ("BOX",(0,0),(-1,-1),0.5,BORDER),
        ]))
        return t

    def bcard(items):
        return card(*[Paragraph(t, s_bul) for (t,) in bul(items)])

    def rule(): return HRFlowable(width="100%",thickness=0.5,color=BORDER,spaceAfter=8,spaceBefore=5)

    story = []

    # Header
    h = Table([[Paragraph("SOAP NOTE",s_ht)],[Paragraph("HeyDoc · AI Medical Scribe",s_sub)],[Paragraph(today,s_sub)]],colWidths=[doc.width])
    h.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),DARK),("TOPPADDING",(0,0),(-1,-1),10),
        ("BOTTOMPADDING",(0,0),(-1,-1),10),("LEFTPADDING",(0,0),(-1,-1),16),("ROUNDEDCORNERS",[7]),
        ("BOX",(0,0),(-1,-1),1,colors.HexColor("#2A2B2E"))]))
    story += [h, Spacer(1,8)]

    # Warning
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
        Paragraph(f"HeyDoc AI Medical Scribe  ·  {today}  ·  All AI-generated notes must be reviewed by a licensed clinician before clinical use",s_ftr)]

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

def generate_followup_reminder(soap, api_key, patient_name="Patient"):
    client = get_client(api_key)
    pl = soap.get("plan",{})
    prompt = f"""Write a brief friendly SMS-style follow-up reminder (<120 words).
Start with "Hi {patient_name}," Include next steps, return date, who to call.
Follow-up: {pl.get('follow_up')} Tests: {pl.get('investigations',[])} Meds: {pl.get('medications',[])}"""
    try:
        r = client.chat.completions.create(model=MODEL,messages=[{"role":"user","content":prompt}],max_tokens=200)
        return r.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate reminder: {e}"

def log_event(action, patient_name, details):
    entry = {"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
             "action": action, "patient": patient_name, **details}
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

def send_via_email(pdf_bytes, to_email, smtp_host, smtp_port, sender_email, sender_password, patient_name="Patient"):
    try:
        msg = EmailMessage()
        msg["Subject"] = f"SOAP Note — {patient_name} — {datetime.date.today()}"
        msg["From"] = sender_email; msg["To"] = to_email
        msg.set_content(f"SOAP note for {patient_name}.\nGenerated by HeyDoc AI Medical Scribe. Review before clinical use.")
        msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf",
                           filename=f"soap_{patient_name.replace(' ','_')}_{datetime.date.today()}.pdf")
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

# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════

# ── PAGE 1: Record & Transcribe ───────────────────────────────────────────────
if page == "Record & Transcribe":
    page_header("🎙", "Record & Transcribe",
                "Capture audio or paste a transcript to generate your SOAP note")

    t1, t2, t3 = st.tabs(["Record", "Upload File", "Paste Transcript"])
    recorded_audio = None
    audio_file = None

    with t1:
        st.markdown("<br>", unsafe_allow_html=True)
        recorded_audio = st.audio_input("", key="mic_input", label_visibility="collapsed")
        if recorded_audio:
            st.audio(recorded_audio, format="audio/wav")
            st.caption("✓ Recording captured — click Generate below")
        else:
            st.caption("Click the microphone to begin recording")

    with t2:
        st.markdown("<br>", unsafe_allow_html=True)
        audio_file = st.file_uploader("", type=["wav","mp3","m4a"], label_visibility="collapsed")
        if audio_file:
            st.audio(audio_file)
            st.caption("✓ File ready")
        else:
            st.caption("Accepts WAV · MP3 · M4A")

    with t3:
        st.markdown("<br>", unsafe_allow_html=True)
        transcript_input = st.text_area(
            "", value=SAMPLE_TRANSCRIPT, height=260,
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
        for k in ["icd10_codes", "followup_reminder"]:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state.raw_transcript = ""
        st.session_state.diarized_transcript = ""
        st.session_state.soap_markdown = ""
        st.session_state.patient_summary = ""
        st.session_state.soap_pdf_bytes = b""
        st.session_state.soap_dict = {}
        st.session_state.pipeline_ran = False
        st.rerun()

    if run_clicked:
        active_audio = recorded_audio or audio_file or None
        try:
            with st.spinner("Processing consultation…"):
                tx = transcript_input if "transcript_input" in dir() else SAMPLE_TRANSCRIPT
                (st.session_state.raw_transcript, st.session_state.diarized_transcript,
                 st.session_state.soap_markdown, st.session_state.patient_summary,
                 st.session_state.soap_pdf_bytes, st.session_state.soap_dict) = run_pipeline(active_audio, tx)
            st.session_state.pipeline_ran = True
            log_event("GENERATED", "Patient", {"source":"pipeline","provider":"—","message_id":"—"})
            st.success("Note generated — navigate with the sidebar")
        except Exception as exc:
            st.error(str(exc))

    # Stats
    if st.session_state.pipeline_ran and st.session_state.diarized_transcript:
        lines  = st.session_state.diarized_transcript.strip().splitlines()
        doc_t  = sum(1 for l in lines if l.startswith("DOCTOR:"))
        pat_t  = sum(1 for l in lines if l.startswith("PATIENT:"))
        words  = len(st.session_state.raw_transcript.split())
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{doc_t}</div><div class="metric-lbl">Doctor turns</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{pat_t}</div><div class="metric-lbl">Patient turns</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{words}</div><div class="metric-lbl">Total words</div></div>', unsafe_allow_html=True)

    if st.session_state.raw_transcript:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("Raw transcript"):
            st.text_area("", value=st.session_state.raw_transcript, height=180,
                         disabled=True, label_visibility="collapsed")

    if st.session_state.diarized_transcript:
        with st.expander("Speaker diarization"):
            html = []
            for line in st.session_state.diarized_transcript.strip().splitlines():
                if line.startswith("DOCTOR:"):
                    html.append(f'<div class="sp-line"><span class="sp-tag doc">Dr</span><span class="sp-speech">{line[7:].strip()}</span></div>')
                elif line.startswith("PATIENT:"):
                    html.append(f'<div class="sp-line"><span class="sp-tag pat">Pt</span><span class="sp-speech">{line[8:].strip()}</span></div>')
                else:
                    html.append(f'<div class="sp-line"><span class="sp-speech" style="color:#5C5850">{line}</span></div>')
            st.markdown("<div style='padding:4px 0'>" + "".join(html) + "</div>", unsafe_allow_html=True)

# ── PAGE 2: SOAP Note ─────────────────────────────────────────────────────────
elif page == "SOAP Note":
    page_header("📋", "SOAP Note", "AI-generated clinical documentation")

    if not st.session_state.pipeline_ran:
        empty_state("Go to Record & Transcribe to generate a note first.")
    else:
        st.markdown('<div class="warn-banner">⚠  AI-generated draft — review and verify before adding to the medical record or sharing with third parties.</div>', unsafe_allow_html=True)
        st.markdown(st.session_state.soap_markdown)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.session_state.soap_pdf_bytes:
            st.download_button("↓  Download PDF", data=st.session_state.soap_pdf_bytes,
                               file_name="soap_note.pdf", mime="application/pdf", use_container_width=True)

# ── PAGE 3: Patient Summary ───────────────────────────────────────────────────
elif page == "Patient Summary":
    page_header("👤", "Patient Summary", "Plain-language visit summary for the patient")

    if not st.session_state.pipeline_ran:
        empty_state()
    else:
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
        patient_name = st.text_input("Patient name", value="Patient", placeholder="e.g. Rahul Sharma")
        if st.button("✦  Generate Reminder", type="primary"):
            with st.spinner("Generating…"):
                reminder = generate_followup_reminder(
                    st.session_state.soap_dict, OPENROUTER_API_KEY, patient_name)
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
        c1, c2 = st.columns(2)
        with c1:
            recipient_name = st.text_input("Recipient name", placeholder="Dr. Smith / City Hospital")
            fax_number     = st.text_input("Fax number", placeholder="+1XXXXXXXXXX")
        with c2:
            email_addr     = st.text_input("Email (optional)", placeholder="doctor@hospital.com")
            recipient_type = st.selectbox("Recipient type",
                ["Hospital / Specialist", "Lab", "Insurance", "Clinic", "Patient"])

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
            recipient = {"name":recipient_name,"type":recipient_type,"fax":fax_number,"email":email_addr}
            with st.spinner("Transmitting…"):
                if method == "Mock (test)":
                    result = send_with_retry(send_via_mock, retries=2,
                                             pdf_bytes=st.session_state.soap_pdf_bytes, recipient=recipient)
                elif method == "Kno2 Fax":
                    result = send_via_kno2(st.session_state.soap_pdf_bytes, fax_number)
                elif method == "Email" and sender_email:
                    result = send_with_retry(send_via_email, retries=2,
                                             pdf_bytes=st.session_state.soap_pdf_bytes,
                                             to_email=email_addr or sender_email,
                                             smtp_host=smtp_host, smtp_port=int(smtp_port),
                                             sender_email=sender_email, sender_password=sender_password,
                                             patient_name=recipient_name)
                else:
                    st.warning("Please fill in all required fields."); result = None

            if result:
                log_event("SENT" if result["success"] else "FAILED", recipient_name,
                          {"provider":result.get("provider"),"message_id":result.get("message_id"),"recipient":recipient_name})
                if result["success"]:
                    st.success(f"Transmitted successfully · ID: {result['message_id']}")
                else:
                    st.error(f"Transmission failed · {result.get('error','Unknown error')}")

# ── PAGE 7: Sessions ──────────────────────────────────────────────────────────
elif page == "Sessions":
    page_header("👥", "Sessions", "Today's patient records")

    sessions = st.session_state.patient_sessions

    if st.session_state.pipeline_ran:
        with st.expander("Save current note to sessions"):
            name = st.text_input("Patient name", placeholder="e.g. John Doe", key="save_name")
            if st.button("Save Session", type="primary", key="save_btn"):
                entry = {
                    "id": len(sessions)+1,
                    "name": name or f"Patient {len(sessions)+1}",
                    "timestamp": datetime.datetime.now().strftime("%H:%M"),
                    "soap": st.session_state.soap_dict,
                    "pdf_bytes": st.session_state.soap_pdf_bytes,
                    "summary": st.session_state.patient_summary,
                    "diagnosis": st.session_state.soap_dict.get("assessment",{}).get("diagnosis","—"),
                }
                sessions.append(entry)
                log_event("GENERATED", entry["name"],
                          {"diagnosis":entry["diagnosis"],"provider":"—","message_id":"—"})
                st.success("Session saved")

    st.markdown("<br>", unsafe_allow_html=True)

    if not sessions:
        empty_state("No sessions saved yet. Run the pipeline and save a session.")
    else:
        for s in reversed(sessions):
            with st.expander(f"{s['name']}  ·  {s['timestamp']}  ·  {s['diagnosis']}"):
                c1, c2 = st.columns([3,1])
                with c1:
                    st.markdown(f"**Diagnosis:** {s['diagnosis']}")
                    summary_preview = s['summary'][:220] + "…" if len(s['summary']) > 220 else s['summary']
                    st.markdown(f"**Summary:** {summary_preview}")
                with c2:
                    if s["pdf_bytes"]:
                        st.download_button("↓ PDF", data=s["pdf_bytes"],
                                           file_name=f"soap_{s['name'].replace(' ','_')}.pdf",
                                           mime="application/pdf", key=f"dl_{s['id']}",
                                           use_container_width=True)

# ── PAGE 8: Audit Log ─────────────────────────────────────────────────────────
elif page == "Audit Log":
    page_header("🗂", "Audit Log", "All actions recorded in this session")

    log = st.session_state.audit_log
    if not log:
        empty_state("No events logged yet.")
    else:
        action_colors = {
            "GENERATED": "#C9A96E",
            "SENT":      "#4ADE80",
            "FAILED":    "#F87171",
            "DOWNLOADED":"#A78BFA",
            "VIEWED":    "#60A5FA",
        }

        st.markdown("""
        <div class="audit-grid" style="color:#5C5850;font-size:0.68rem;text-transform:uppercase;
             letter-spacing:0.12em;font-weight:700;border-bottom:1px solid rgba(255,255,255,0.1);padding-bottom:6px;">
            <span>Time</span><span>Action</span><span>Patient</span><span>Provider</span>
        </div>""", unsafe_allow_html=True)

        for entry in reversed(log[-30:]):
            c = action_colors.get(entry.get("action",""), "#5C5850")
            st.markdown(f"""
            <div class="audit-grid">
                <span class="audit-ts">{entry.get('timestamp','')}</span>
                <span class="audit-act" style="color:{c};font-weight:600;font-size:0.77rem;">
                    {entry.get('action','')}</span>
                <span class="audit-pat">{entry.get('patient','—')}</span>
                <span class="audit-prv">{entry.get('provider','—')}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        buf = io.StringIO()
        all_keys = set()
        for e in log: all_keys.update(e.keys())
        w = csv.DictWriter(buf, fieldnames=list(all_keys))
        w.writeheader()
        [w.writerow(e) for e in log]
        st.download_button("↓  Export Audit Log CSV", data=buf.getvalue().encode(),
                           file_name=f"heydoc_audit_{datetime.date.today()}.csv", mime="text/csv")

# ── Disclaimer ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
    <strong>Clinical Disclaimer</strong> — All AI-generated notes must be reviewed by a licensed
    clinician before clinical use. HeyDoc is an AI assistant, not a substitute for clinical judgment.
    Do not enter patient-identifiable data in demo environments.
</div>
""", unsafe_allow_html=True)
