"""
app.py – NetSage AI: Enterprise Network Intelligence Platform.

Premium redesign with electric blue accent palette, Linear/Datadog-inspired
design system, glassmorphism cards, and animated micro-interactions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from modules.csv_manager import load_cases, get_review_stats
from modules.ai_engine import is_api_key_configured

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="NetSage AI – Enterprise Network Diagnostics",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/Lucky-Chauhan-py/NetSage-AI",
        "About": "NetSage AI Enterprise v2.5 – AI-Powered Cisco Troubleshooting Platform",
    },
)

# ---------------------------------------------------------------------------
# Master Design System CSS
# ---------------------------------------------------------------------------

GLOBAL_CSS = """
<style>
/* ── Fonts ──────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Design Tokens ──────────────────────────────────────────────────────── */
:root {
    --bg-base:       #07080A;
    --bg-surface:    #0D0F12;
    --bg-elevated:   #131619;
    --bg-overlay:    #1A1D22;
    --border-subtle: rgba(255,255,255,0.07);
    --border-medium: rgba(255,255,255,0.13);
    --border-strong: rgba(255,255,255,0.22);
    --accent-blue:   #3B82F6;
    --accent-blue-2: #60A5FA;
    --accent-green:  #10B981;
    --accent-green-2:#34D399;
    --accent-amber:  #F59E0B;
    --accent-rose:   #F43F5E;
    --accent-purple: #8B5CF6;
    --text-primary:  #F1F5F9;
    --text-secondary:#94A3B8;
    --text-muted:    #475569;
    --text-disabled: #334155;
}

/* ── Global Reset ────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif !important;
}
h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.025em;
}
code, pre, .stCode {
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── App Background ──────────────────────────────────────────────────────── */
.stApp {
    background: var(--bg-base) !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59,130,246,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(16,185,129,0.04) 0%, transparent 50%) !important;
    background-attachment: fixed !important;
    color: var(--text-primary) !important;
}

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: #1E2530; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #2D3748; }

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border-subtle) !important;
    box-shadow: 1px 0 0 var(--border-subtle);
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: var(--text-secondary);
    font-size: 0.85rem;
}
[data-testid="stSidebar"] a {
    border-radius: 8px !important;
    padding: 9px 14px !important;
    margin-bottom: 3px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    color: var(--text-secondary) !important;
    transition: all 0.18s ease !important;
    border: 1px solid transparent !important;
}
[data-testid="stSidebar"] a:hover {
    background: var(--bg-elevated) !important;
    border-color: var(--border-subtle) !important;
    color: var(--text-primary) !important;
}

/* ── Cards ───────────────────────────────────────────────────────────────── */
.ns-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 16px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
}
.ns-card:hover {
    border-color: var(--border-medium);
    box-shadow: 0 8px 32px -8px rgba(0,0,0,0.6);
}
.ns-card-blue {
    border-top: 2px solid var(--accent-blue);
    box-shadow: 0 0 0 1px var(--border-subtle), 0 4px 24px -4px rgba(59,130,246,0.12);
}
.ns-card-green {
    border-top: 2px solid var(--accent-green);
    box-shadow: 0 0 0 1px var(--border-subtle), 0 4px 24px -4px rgba(16,185,129,0.10);
}
.ns-card-amber {
    border-top: 2px solid var(--accent-amber);
    box-shadow: 0 0 0 1px var(--border-subtle), 0 4px 24px -4px rgba(245,158,11,0.10);
}
.ns-card-rose {
    border-top: 2px solid var(--accent-rose);
    box-shadow: 0 0 0 1px var(--border-subtle), 0 4px 24px -4px rgba(244,63,94,0.10);
}
.ns-card-purple {
    border-top: 2px solid var(--accent-purple);
    box-shadow: 0 0 0 1px var(--border-subtle), 0 4px 24px -4px rgba(139,92,246,0.10);
}

/* ── Metric / KPI Cards ──────────────────────────────────────────────────── */
.kpi-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 20px 18px;
    text-align: center;
    transition: all 0.2s ease;
}
.kpi-card:hover {
    border-color: var(--border-medium);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px -6px rgba(0,0,0,0.5);
}
.kpi-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.1;
    margin-bottom: 4px;
}
.kpi-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-weight: 600;
}
.kpi-delta {
    font-size: 0.78rem;
    color: var(--accent-green-2);
    font-weight: 600;
    margin-top: 4px;
}

/* ── Hero Section ────────────────────────────────────────────────────────── */
.hero-section {
    padding: 48px 0 36px;
    margin-bottom: 8px;
}
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.25);
    color: var(--accent-blue-2);
    border-radius: 100px;
    padding: 5px 14px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    margin-bottom: 20px;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.1;
    letter-spacing: -0.04em;
    margin-bottom: 14px;
}
.hero-title span {
    background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-blue-2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-desc {
    font-size: 1.05rem;
    color: var(--text-secondary);
    max-width: 700px;
    line-height: 1.7;
    font-weight: 400;
}

/* ── Section Headers ─────────────────────────────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-subtle);
}
.section-header-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}
.section-header-sub {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-left: auto;
    font-weight: 500;
}

/* ── Pipeline Steps ──────────────────────────────────────────────────────── */
.pipeline-step {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 18px 16px;
    height: 175px;
    transition: all 0.2s ease;
    position: relative;
}
.pipeline-step:hover {
    border-color: var(--border-medium);
    background: var(--bg-elevated);
}
.pipeline-step-num {
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--text-disabled);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.pipeline-step-icon {
    font-size: 1.5rem;
    margin-bottom: 8px;
    display: block;
}
.pipeline-step-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 6px;
}
.pipeline-step-desc {
    font-size: 0.78rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

/* ── Case Preset Cards ───────────────────────────────────────────────────── */
.case-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 20px;
    height: 160px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.case-card:hover {
    border-color: rgba(59,130,246,0.35);
    box-shadow: 0 4px 20px -4px rgba(59,130,246,0.15);
    transform: translateY(-2px);
}
.case-id {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 6px;
}
.case-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.92rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
}
.case-desc {
    font-size: 0.8rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

/* ── Badges / Pills ──────────────────────────────────────────────────────── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-blue   { background: rgba(59,130,246,0.12);  color: #93C5FD; border: 1px solid rgba(59,130,246,0.25); }
.badge-green  { background: rgba(16,185,129,0.12);  color: #6EE7B7; border: 1px solid rgba(16,185,129,0.25); }
.badge-amber  { background: rgba(245,158,11,0.12);  color: #FCD34D; border: 1px solid rgba(245,158,11,0.25); }
.badge-rose   { background: rgba(244,63,94,0.12);   color: #FDA4AF; border: 1px solid rgba(244,63,94,0.25); }
.badge-purple { background: rgba(139,92,246,0.12);  color: #C4B5FD; border: 1px solid rgba(139,92,246,0.25); }
.badge-slate  { background: rgba(100,116,139,0.12); color: #94A3B8; border: 1px solid rgba(100,116,139,0.25); }

/* ── Status Indicators ───────────────────────────────────────────────────── */
.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
.status-online  { background: var(--accent-green); box-shadow: 0 0 0 2px rgba(16,185,129,0.3); animation: status-pulse 2s infinite; }
.status-offline { background: #EF4444; box-shadow: 0 0 0 2px rgba(239,68,68,0.3); }
.status-warning { background: var(--accent-amber); box-shadow: 0 0 0 2px rgba(245,158,11,0.3); }
@keyframes status-pulse {
    0%, 100% { box-shadow: 0 0 0 2px rgba(16,185,129,0.3); }
    50%       { box-shadow: 0 0 0 5px rgba(16,185,129,0); }
}

/* ── Terminal Window ─────────────────────────────────────────────────────── */
.terminal-window {
    background: #090B0E;
    border: 1px solid var(--border-medium);
    border-radius: 12px;
    overflow: hidden;
    font-family: 'JetBrains Mono', monospace;
    margin: 12px 0;
}
.terminal-titlebar {
    background: var(--bg-elevated);
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 7px;
    border-bottom: 1px solid var(--border-subtle);
}
.t-dot { width: 10px; height: 10px; border-radius: 50%; }
.t-red    { background: #FF5F57; }
.t-yellow { background: #FFBD2E; }
.t-green  { background: #28C840; }
.terminal-label { font-size: 0.75rem; color: var(--text-muted); margin-left: 8px; font-weight: 500; }
.terminal-body {
    padding: 16px 18px;
    color: #4ADE80;
    font-size: 0.84rem;
    line-height: 1.7;
    white-space: pre-wrap;
    min-height: 80px;
}
.t-prompt { color: var(--accent-blue-2); }
.t-dim    { color: var(--text-disabled); }
.t-white  { color: var(--text-primary); }
.t-warn   { color: #FBBF24; }
.t-err    { color: #F87171; }

/* ── Buttons ─────────────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: var(--bg-overlay) !important;
    border-color: var(--border-strong) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: var(--accent-blue) !important;
    color: #FFFFFF !important;
    border-color: var(--accent-blue) !important;
    box-shadow: 0 1px 3px rgba(59,130,246,0.4) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #2563EB !important;
    border-color: #2563EB !important;
    box-shadow: 0 4px 16px rgba(59,130,246,0.4) !important;
}

/* ── Inputs ──────────────────────────────────────────────────────────────── */
.stTextArea textarea, .stTextInput input {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-medium) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.875rem !important;
    transition: border-color 0.18s ease !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}
.stSelectbox > div > div {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}

/* ── Tabs ────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-surface) !important;
    border-radius: 10px !important;
    padding: 5px !important;
    gap: 4px !important;
    border: 1px solid var(--border-subtle) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    padding: 7px 16px !important;
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    transition: all 0.15s ease !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-medium) !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3) !important;
}

/* ── Dataframes / Tables ─────────────────────────────────────────────────── */
.stDataFrame { border: 1px solid var(--border-subtle) !important; border-radius: 10px !important; overflow: hidden; }

/* ── Divider ─────────────────────────────────────────────────────────────── */
hr { border-color: var(--border-subtle) !important; margin: 28px 0 !important; }

/* ── Hide Streamlit Boilerplate ──────────────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Fade-in Animation ───────────────────────────────────────────────────── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp 0.45s ease forwards; }

/* ── Protocol tag cloud ──────────────────────────────────────────────────── */
.tag-cloud { display: flex; flex-wrap: wrap; gap: 8px; }
.tag {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    color: var(--text-secondary);
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 0.78rem;
    font-weight: 500;
    transition: all 0.15s ease;
    font-family: 'JetBrains Mono', monospace;
}
.tag:hover {
    border-color: rgba(59,130,246,0.4);
    color: var(--accent-blue-2);
    background: rgba(59,130,246,0.06);
}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    # Logo
    st.markdown("""
<div style="padding:20px 8px 16px; border-bottom:1px solid rgba(255,255,255,0.07); margin-bottom:16px;">
    <div style="display:flex; align-items:center; gap:10px;">
        <div style="
            width:36px; height:36px; border-radius:9px; flex-shrink:0;
            background:linear-gradient(135deg, #3B82F6 0%, #10B981 100%);
            display:flex; align-items:center; justify-content:center;
            font-size:1.1rem; box-shadow:0 4px 12px rgba(59,130,246,0.4);">
            🛰️
        </div>
        <div>
            <div style="font-family:'Space Grotesk',sans-serif; font-size:1.05rem; font-weight:800; color:#F1F5F9; letter-spacing:-0.02em;">NetSage AI</div>
            <div style="font-size:0.68rem; color:#475569; font-weight:500; letter-spacing:0.04em; text-transform:uppercase;">Enterprise v2.5</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # Engine Status
    api_ok = is_api_key_configured()
    if api_ok:
        st.markdown("""
<div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.2); border-radius:10px; padding:10px 14px; margin-bottom:18px;">
    <div style="display:flex; align-items:center; gap:8px;">
        <span class="status-dot status-online"></span>
        <span style="font-size:0.82rem; font-weight:600; color:#34D399; font-family:'Inter',sans-serif;">Gemini AI Online</span>
    </div>
    <div style="font-size:0.72rem; color:#475569; margin-top:3px; padding-left:16px;">gemini-3.6-flash • Connected</div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.2); border-radius:10px; padding:10px 14px; margin-bottom:18px;">
    <div style="display:flex; align-items:center; gap:8px;">
        <span class="status-dot status-warning"></span>
        <span style="font-size:0.82rem; font-weight:600; color:#FCD34D; font-family:'Inter',sans-serif;">Offline Mode</span>
    </div>
    <div style="font-size:0.72rem; color:#475569; margin-top:3px; padding-left:16px;">Rule Engine Active • No API Key</div>
</div>
""", unsafe_allow_html=True)
        with st.expander("🔑 Add API Key", expanded=False):
            key_input = st.text_input("Gemini API Key", type="password", placeholder="AIzaSy...")
            if key_input:
                import os
                os.environ["GEMINI_API_KEY"] = key_input.strip()
                st.success("Key activated!")
                st.rerun()

    # Navigation
    st.markdown('<div style="font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.09em; color:#334155; margin-bottom:6px;">Navigation</div>', unsafe_allow_html=True)
    st.page_link("app.py",                       label="⌂  Command Center",       use_container_width=True)
    st.page_link("pages/1_AI_Diagnosis.py",       label="◎  AI Diagnosis",         use_container_width=True)
    st.page_link("pages/2_Human_Review.py",       label="◈  Human Review Board",   use_container_width=True)
    st.page_link("pages/3_Dashboard.py",          label="▦  Analytics Dashboard",  use_container_width=True)
    st.page_link("pages/4_Dataset_Manager.py",    label="⊞  Dataset Manager",      use_container_width=True)
    st.page_link("pages/5_About.py",              label="◉  Architecture & Docs",  use_container_width=True)

    st.markdown("""
<div style="margin-top:auto; padding:16px 8px 8px; border-top:1px solid rgba(255,255,255,0.06); margin-top:24px;">
    <div style="font-size:0.7rem; color:#334155; line-height:1.6; text-align:center;">
        NetSage AI Platform<br>
        <a href="https://github.com/Lucky-Chauhan-py/NetSage-AI" style="color:#3B82F6; text-decoration:none;">GitHub ↗</a>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main Content – Command Center
# ---------------------------------------------------------------------------

# ── Hero ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section fade-up">
    <div class="hero-eyebrow">🛰️ &nbsp; AI-Powered &nbsp;·&nbsp; Cisco Packet Tracer Labs &nbsp;·&nbsp; Human-in-the-Loop</div>
    <div class="hero-title">NetSage <span>AI</span> Command Center</div>
    <div class="hero-desc">
        Enterprise-grade autonomous troubleshooting for Cisco network labs.
        14 deterministic rules + Gemini LLM diagnostics with mandatory human review guardrails.
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────
try:
    cases_df  = load_cases()
    stats     = get_review_stats()
    total_cases   = len(cases_df)
    total_reviews = stats["total"]
    ai_accuracy   = stats["ai_agreement_pct"]
    most_common   = (
        cases_df["concept_tag"].value_counts().index[0]
        if not cases_df.empty and "concept_tag" in cases_df.columns else "VLAN"
    )
except Exception:
    total_cases, total_reviews, ai_accuracy, most_common = 30, 0, 100.0, "VLAN"

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
<div class="kpi-card">
    <div style="font-size:0.75rem; color:#3B82F6; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:8px;">📁 Knowledge Base</div>
    <div class="kpi-value">{total_cases}</div>
    <div class="kpi-label">Troubleshooting Cases</div>
</div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""
<div class="kpi-card">
    <div style="font-size:0.75rem; color:#10B981; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:8px;">⚙️ Rule Matrix</div>
    <div class="kpi-value">14</div>
    <div class="kpi-label">Deterministic Rules</div>
</div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""
<div class="kpi-card">
    <div style="font-size:0.75rem; color:#8B5CF6; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:8px;">👤 Reviews</div>
    <div class="kpi-value">{total_reviews}</div>
    <div class="kpi-label">Human Reviews Logged</div>
</div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""
<div class="kpi-card">
    <div style="font-size:0.75rem; color:#F59E0B; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:8px;">📡 Top Fault</div>
    <div class="kpi-value" style="font-size:1.4rem;">{most_common}</div>
    <div class="kpi-label">Primary Fault Vector</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Diagnostic Pipeline ────────────────────────────────────────────────────
st.markdown("""
<div class="section-header">
    <span class="section-header-title">Autonomous Diagnostic Pipeline</span>
    <span class="section-header-sub">5-stage AI-assisted workflow</span>
</div>
""", unsafe_allow_html=True)

p1, p2, p3, p4, p5 = st.columns(5)
pipeline = [
    ("01", "📋", "Telemetry Input",    "blue",   "Paste Cisco CLI show output and describe the topology symptom."),
    ("02", "⚙️", "Rule Checker",       "green",  "14 deterministic rules instantly scan for L1–L3 faults."),
    ("03", "🤖", "Gemini AI Engine",   "purple", "LLM analyzes OSI layers and generates structured fix steps."),
    ("04", "👤", "Human Review",       "amber",  "Mandatory engineer approval: Accept, Edit, or Reject."),
    ("05", "📊", "Audit & Analytics",  "rose",   "All decisions logged for AI accuracy tracking and learning."),
]
cols = [p1, p2, p3, p4, p5]
for col, (num, icon, title, color, desc) in zip(cols, pipeline):
    border_color = {
        "blue":"#3B82F6","green":"#10B981","purple":"#8B5CF6","amber":"#F59E0B","rose":"#F43F5E"
    }[color]
    with col:
        st.markdown(f"""
<div class="pipeline-step" style="border-top:2px solid {border_color};">
    <div class="pipeline-step-num">Step {num}</div>
    <span class="pipeline-step-icon">{icon}</span>
    <div class="pipeline-step-title">{title}</div>
    <div class="pipeline-step-desc">{desc}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Demo Case Presets ──────────────────────────────────────────────────────
st.markdown("""
<div class="section-header">
    <span class="section-header-title">Demo Lab Cases</span>
    <span class="section-header-sub">Copy presets into AI Diagnosis →</span>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
cases = [
    ("CASE-001", "Layer 1 · Physical", "Interface Shutdown",
     "PC0 cannot ping gateway. Router0 Gi0/0 is administratively shut down.", "rose"),
    ("CASE-005", "Layer 3 · Routing",  "Missing Static Route",
     "Inter-VLAN traffic blocked. Subinterface missing from Router-on-a-Stick config.", "blue"),
    ("CASE-012", "Layer 2 · Switching","Trunk Misconfiguration",
     "Switch uplink configured as access port instead of 802.1Q trunk.", "purple"),
]
for col, (cid, layer, title, desc, color) in zip([c1, c2, c3], cases):
    accent = {"rose":"#FDA4AF","blue":"#93C5FD","purple":"#C4B5FD"}[color]
    badge_cls = f"badge-{color}"
    with col:
        st.markdown(f"""
<div class="case-card">
    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
        <div class="case-id">{cid}</div>
        <span class="badge {badge_cls}">{layer}</span>
    </div>
    <div class="case-title">{title}</div>
    <div class="case-desc">{desc}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick Launch ───────────────────────────────────────────────────────────
st.markdown("""
<div class="section-header">
    <span class="section-header-title">Quick Launch</span>
</div>
""", unsafe_allow_html=True)

ql1, ql2, ql3, ql4 = st.columns(4)
with ql1:
    st.page_link("pages/1_AI_Diagnosis.py",    label="◎  AI Diagnosis Console",   use_container_width=True)
with ql2:
    st.page_link("pages/2_Human_Review.py",    label="◈  Human Review Queue",     use_container_width=True)
with ql3:
    st.page_link("pages/3_Dashboard.py",       label="▦  Analytics Dashboard",    use_container_width=True)
with ql4:
    st.page_link("pages/4_Dataset_Manager.py", label="⊞  Dataset Manager",        use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Protocol Coverage ──────────────────────────────────────────────────────
st.markdown("""
<div class="section-header">
    <span class="section-header-title">Protocol & Fault Coverage</span>
    <span class="section-header-sub">13 fault vectors across OSI L1–L7</span>
</div>
""", unsafe_allow_html=True)

protocols = [
    "VLAN Trunking (802.1Q)", "DHCP Relay Agent", "DNS Resolution",
    "OSPF Area 0", "Static Routing", "NAT Overload (PAT)", "Port Security",
    "Inter-VLAN (RoAS)", "Subnet Masking", "Default Gateway", "Interface Shutdown",
    "Duplicate IP", "ACL Rule Matrix"
]
tags_html = "".join([f'<span class="tag">{p}</span>' for p in protocols])
st.markdown(f'<div class="ns-card"><div class="tag-cloud">{tags_html}</div></div>', unsafe_allow_html=True)
