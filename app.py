"""
app.py – NetSage AI: Enterprise Network Intelligence Platform.

Main entry point configuring ultra-sleek Vercel/Obsidian Black & White design system,
global CSS, sidebar status, and interactive Command Center dashboard.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path so 'modules' can be imported from pages/
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from modules.csv_manager import load_cases, get_review_stats
from modules.ai_engine import is_api_key_configured, get_api_key

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="NetSage AI Enterprise – Cisco Troubleshooting System",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com",
        "About": "NetSage AI Enterprise v2.4 – Autonomous Cisco Troubleshooting Assistant",
    },
)

# ---------------------------------------------------------------------------
# Master CSS System (Obsidian & Crisp White Vercel Theme)
# ---------------------------------------------------------------------------

GLOBAL_CSS = """
<style>
/* ── Google Fonts ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* ── Global Canvas & Obsidian Background ──────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: -0.03em;
}

.stApp {
    background: #000000 !important;
    background-image: 
        radial-gradient(circle at 50% 0%, #1A1A1A 0%, #0A0A0A 65%, #000000 100%),
        radial-gradient(at 100% 100%, #121212 0px, transparent 50%) !important;
    background-attachment: fixed !important;
    color: #FAFAFA !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #000000;
}
::-webkit-scrollbar-thumb {
    background: #333333;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #555555;
}

/* ── Sidebar Styling ──────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #050505 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
    box-shadow: 4px 0 30px rgba(0, 0, 0, 0.8);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #A3A3A3;
}

/* Sidebar Nav Links */
[data-testid="stSidebar"] a {
    border-radius: 12px !important;
    padding: 11px 16px !important;
    margin-bottom: 5px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.01em !important;
    color: #D4D4D4 !important;
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: 1px solid transparent !important;
}
[data-testid="stSidebar"] a:hover {
    background: #171717 !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
    color: #FFFFFF !important;
    transform: translateX(4px);
    box-shadow: 0 4px 15px rgba(255, 255, 255, 0.05);
}

/* ── Glassmorphic Cards (Obsidian & White Border) ─────────────────────── */
.netsage-card {
    background: rgba(18, 18, 18, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 20px;
    padding: 26px;
    margin-bottom: 22px;
    box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.9), inset 0 1px 0 rgba(255, 255, 255, 0.12);
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}
.netsage-card:hover {
    border-color: rgba(255, 255, 255, 0.35);
    box-shadow: 0 20px 40px -10px rgba(255, 255, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.25);
    transform: translateY(-3px);
}

.netsage-card-glow {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(20, 20, 20, 0.9) 100%);
    border: 1px solid rgba(255, 255, 255, 0.25);
    box-shadow: 0 15px 40px -10px rgba(255, 255, 255, 0.12);
}

/* ── KPI Stat Cards ───────────────────────────────────────────────────── */
.metric-card {
    background: #0F0F0F;
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 16px;
    padding: 22px 18px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 8px 25px -5px rgba(0, 0, 0, 0.7);
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #FFFFFF, #737373, #FFFFFF);
    opacity: 0.9;
}
.metric-card:hover {
    border-color: rgba(255, 255, 255, 0.4);
    box-shadow: 0 12px 30px -5px rgba(255, 255, 255, 0.12);
    transform: translateY(-4px);
}
.metric-value {
    font-family: 'Outfit', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    color: #FFFFFF !important;
    background: linear-gradient(135deg, #FFFFFF 0%, #E5E5E5 50%, #A3A3A3 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
    margin-bottom: 6px;
}
.metric-label {
    font-size: 0.78rem;
    color: #A3A3A3;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}

/* ── Hero Banner ──────────────────────────────────────────────────────── */
.hero-banner {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.07) 0%, rgba(23, 23, 23, 0.9) 100%);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.22);
    border-radius: 24px;
    padding: 42px 36px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 50px -15px rgba(0, 0, 0, 0.9), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}
.hero-banner::after {
    content: '';
    position: absolute;
    top: -50%; right: -20%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: 3.3rem;
    font-weight: 900;
    color: #FFFFFF;
    background: linear-gradient(135deg, #FFFFFF 0%, #F5F5F5 50%, #D4D4D4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.12;
    margin-bottom: 14px;
}
.hero-subtitle {
    font-size: 1.15rem;
    color: #D4D4D4;
    max-width: 850px;
    line-height: 1.65;
    font-weight: 400;
}

/* ── Warp / Vercel Style Terminal ─────────────────────────────────────── */
.terminal-window {
    background: #050505;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.9);
    font-family: 'JetBrains Mono', monospace;
    margin: 14px 0;
}
.terminal-header {
    background: #121212;
    padding: 10px 18px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.dot { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }
.dot-red { background: #FF5F56; box-shadow: 0 0 8px rgba(255, 95, 86, 0.5); }
.dot-yellow { background: #FFBD2E; box-shadow: 0 0 8px rgba(255, 189, 46, 0.5); }
.dot-green { background: #27C93F; box-shadow: 0 0 8px rgba(39, 201, 63, 0.5); }
.terminal-title { font-size: 0.78rem; color: #A3A3A3; margin-left: 8px; font-weight: 600; letter-spacing: 0.02em; }
.terminal-body {
    padding: 18px 20px;
    color: #10B981;
    font-size: 0.88rem;
    line-height: 1.65;
    white-space: pre-wrap;
}

/* ── Badges ───────────────────────────────────────────────────────────── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}
.badge-blue   { background: rgba(255, 255, 255, 0.1); color: #FFFFFF; border: 1px solid rgba(255, 255, 255, 0.25); }
.badge-green  { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.35); }
.badge-purple { background: rgba(255, 255, 255, 0.12); color: #E5E5E5; border: 1px solid rgba(255, 255, 255, 0.25); }
.badge-amber  { background: rgba(245, 158, 11, 0.15);  color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.35); }
.badge-rose   { background: rgba(244, 63, 94, 0.15);   color: #FB7185; border: 1px solid rgba(244, 63, 94, 0.35); }

/* Pulse Indicator */
.pulse-dot {
    width: 9px; height: 9px; border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.8);
    animation: pulse 1.8s infinite;
}
.pulse-dot-cyan {
    width: 9px; height: 9px; border-radius: 50%;
    background: #FFFFFF;
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.8);
    animation: pulse-white 1.8s infinite;
}
@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.8); }
    70% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}
@keyframes pulse-white {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.8); }
    70% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(255, 255, 255, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); }
}

/* ── High-Contrast Vercel-Style Buttons ───────────────────────────────── */
.stButton > button {
    background: #171717 !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
    padding: 0.65rem 1.6rem !important;
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5) !important;
}
.stButton > button:hover {
    background: #262626 !important;
    border-color: #FFFFFF !important;
    color: #FFFFFF !important;
    box-shadow: 0 8px 25px rgba(255, 255, 255, 0.2) !important;
    transform: translateY(-2px) !important;
}

/* Primary Form Button (Crisp White Button like Vercel) */
.stButton > button[kind="primary"] {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #FFFFFF !important;
    box-shadow: 0 4px 20px rgba(255, 255, 255, 0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #E5E5E5 !important;
    color: #000000 !important;
    box-shadow: 0 8px 30px rgba(255, 255, 255, 0.5) !important;
}

/* ── Input Fields & Selectboxes ───────────────────────────────────────── */
.stTextArea textarea, .stTextInput input, .stSelectbox select {
    background: #0A0A0A !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: #FFFFFF !important;
    border-radius: 12px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.6) !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #FFFFFF !important;
    box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.25), inset 0 2px 4px rgba(0,0,0,0.6) !important;
}

/* ── Streamlit Tabs Styling ───────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #0D0D0D !important;
    border-radius: 14px !important;
    padding: 6px !important;
    gap: 6px !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    padding: 8px 18px !important;
    color: #A3A3A3 !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #FFFFFF !important;
}

/* ── Dividers ─────────────────────────────────────────────────────────── */
hr {
    border-color: rgba(255, 255, 255, 0.12) !important;
    margin: 32px 0 !important;
}

/* ── Hide Streamlit Default UI ────────────────────────────────────────── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar Design
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div style="padding:12px 4px 18px; text-align:center;">
            <div style="font-size:2.6rem; margin-bottom:4px;">🌐</div>
            <div style="font-family:'Outfit',sans-serif; font-size:1.5rem; font-weight:900; color:#FFFFFF; letter-spacing:-0.02em;">
                NetSage AI
            </div>
            <div style="font-size:0.75rem; color:#A3A3A3; font-weight:600; margin-top:2px; letter-spacing:0.04em;">
                Cisco Autonomous Diagnostic Suite v2.4
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Engine Status Badge
    api_ok = is_api_key_configured()
    if api_ok:
        st.markdown(
            """
            <div style="background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.35); border-radius:14px; padding:12px 16px; margin-bottom:20px; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div class="pulse-dot"></div>
                    <span style="font-size:0.85rem; font-weight:800; color:#34D399; font-family:'Outfit',sans-serif;">Cloud AI Engine Online</span>
                </div>
                <div style="font-size:0.75rem; color:#A3A3A3; margin-top:4px;">Gemini 1.5 Flash • Active</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.25); border-radius:14px; padding:12px 16px; margin-bottom:20px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div class="pulse-dot-cyan"></div>
                    <span style="font-size:0.85rem; font-weight:800; color:#FFFFFF; font-family:'Outfit',sans-serif;">Autonomous Local Engine</span>
                </div>
                <div style="font-size:0.75rem; color:#A3A3A3; margin-top:4px;">14-Rule Matrix + Embedded Diagnostics</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("🔑 Activate Gemini API Key", expanded=False):
            key_input = st.text_input("Enter API Key", type="password", placeholder="AIzaSy...")
            if key_input:
                import os
                os.environ["GEMINI_API_KEY"] = key_input.strip()
                st.success("API Key activated!")
                st.rerun()

    st.markdown("<div style='font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; color:#737373; font-weight:700; margin-bottom:10px;'>Main Modules</div>", unsafe_allow_html=True)
    st.page_link("app.py", label="🏠 Command Center", use_container_width=True)
    st.page_link("pages/1_AI_Diagnosis.py", label="🔍 AI Diagnosis Console", use_container_width=True)
    st.page_link("pages/2_Human_Review.py", label="👤 Human Review Board", use_container_width=True)
    st.page_link("pages/3_Dashboard.py", label="📊 Telemetry & Metrics", use_container_width=True)
    st.page_link("pages/4_Dataset_Manager.py", label="📁 Dataset Operations", use_container_width=True)
    st.page_link("pages/5_About.py", label="ℹ️ Platform Architecture", use_container_width=True)

    st.markdown("<hr style='margin: 20px 0 !important;'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size:0.72rem; color:#737373; text-align:center; line-height:1.5;">
            NetSage AI Platform Enterprise Edition<br>Autonomous Cisco Packet Tracer Intelligence
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Home Page Content (Command Center)
# ---------------------------------------------------------------------------

# Hero Banner
st.markdown(
    """
    <div class="hero-banner">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:12px;">
            <span class="badge badge-blue">🌐 Autonomous Cisco Diagnostics</span>
            <span class="badge badge-green">⚡ Human Guardrail Active</span>
        </div>
        <div class="hero-title">NetSage AI Command Center</div>
        <div class="hero-subtitle">
            Next-generation autonomous troubleshooting assistant for Cisco Packet Tracer labs.
            Combines deterministic rule validation with Gemini LLM deep diagnostics for rapid incident resolution.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Key Stats
try:
    cases_df = load_cases()
    stats = get_review_stats()
    total_cases = len(cases_df)
    total_reviews = stats["total"]
    ai_accuracy = stats["ai_agreement_pct"]
    most_common = (
        cases_df["concept_tag"].value_counts().index[0]
        if not cases_df.empty and "concept_tag" in cases_df.columns
        else "VLAN"
    )
except Exception:
    total_cases, total_reviews, ai_accuracy, most_common = 30, 0, 100.0, "VLAN"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{total_cases}</div>'
        f'<div class="metric-label">Knowledge Base Cases</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{total_reviews}</div>'
        f'<div class="metric-label">Engineers Reviewed</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{ai_accuracy:.0f}%</div>'
        f'<div class="metric-label">AI Acceptance Precision</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value" style="font-size:1.4rem">{most_common}</div>'
        f'<div class="metric-label">Primary Fault Vector</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# System Workflow Steps
st.markdown("### 🔄 Autonomous Diagnostic Pipeline")

wf1, wf2, wf3, wf4, wf5 = st.columns(5)

with wf1:
    st.markdown(
        """
        <div class="metric-card" style="height:190px; text-align:left; padding:18px;">
            <div style="font-size:1.6rem; margin-bottom:8px;">📝</div>
            <div style="font-weight:800; color:#FFFFFF; font-size:0.95rem; margin-bottom:6px; font-family:'Outfit',sans-serif;">1. Telemetry Input</div>
            <div style="color:#A3A3A3; font-size:0.8rem; line-height:1.55;">Ingest CLI <code>show</code> output &amp; lab topology notes.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with wf2:
    st.markdown(
        """
        <div class="metric-card" style="height:190px; text-align:left; padding:18px;">
            <div style="font-size:1.6rem; margin-bottom:8px;">⚙️</div>
            <div style="font-weight:800; color:#34D399; font-size:0.95rem; margin-bottom:6px; font-family:'Outfit',sans-serif;">2. Rule Checker</div>
            <div style="color:#A3A3A3; font-size:0.8rem; line-height:1.55;">14 deterministic rules run instantly to catch physical &amp; L2/L3 errors.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with wf3:
    st.markdown(
        """
        <div class="metric-card" style="height:190px; text-align:left; padding:18px;">
            <div style="font-size:1.6rem; margin-bottom:8px;">🤖</div>
            <div style="font-weight:800; color:#FFFFFF; font-size:0.95rem; margin-bottom:6px; font-family:'Outfit',sans-serif;">3. Gemini Neural AI</div>
            <div style="color:#A3A3A3; font-size:0.8rem; line-height:1.55;">Evaluates OSI layers, synthesizes evidence, generates CLI fix steps.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with wf4:
    st.markdown(
        """
        <div class="metric-card" style="height:190px; text-align:left; padding:18px;">
            <div style="font-size:1.6rem; margin-bottom:8px;">👤</div>
            <div style="font-weight:800; color:#FBBF24; font-size:0.95rem; margin-bottom:6px; font-family:'Outfit',sans-serif;">4. Human Review</div>
            <div style="color:#A3A3A3; font-size:0.8rem; line-height:1.55;">Mandatory engineer review: Accept, Edit, or Reject before deploy.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with wf5:
    st.markdown(
        """
        <div class="metric-card" style="height:190px; text-align:left; padding:18px;">
            <div style="font-size:1.6rem; margin-bottom:8px;">📊</div>
            <div style="font-weight:800; color:#FB7185; font-size:0.95rem; margin-bottom:6px; font-family:'Outfit',sans-serif;">5. Analytics Log</div>
            <div style="color:#A3A3A3; font-size:0.8rem; line-height:1.55;">All reviews logged for AI drift tracking &amp; continuous learning.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Quick Incident Presets Section
st.markdown("### 🧪 Quick Diagnostic Presets (Try Demo Labs)")

preset_col1, preset_col2, preset_col3 = st.columns(3)

with preset_col1:
    st.markdown(
        """
        <div class="netsage-card" style="height:200px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="font-weight:800; color:#FFFFFF; font-family:'Outfit',sans-serif;">CASE-001 · Interface Down</span>
                <span class="badge badge-rose">Layer 1</span>
            </div>
            <div style="font-size:0.85rem; color:#A3A3A3; margin-bottom:16px; line-height:1.5;">
                PC0 cannot ping gateway. Router0 Gi0/0 status is administratively shutdown.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with preset_col2:
    st.markdown(
        """
        <div class="netsage-card" style="height:200px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="font-weight:800; color:#34D399; font-family:'Outfit',sans-serif;">CASE-005 · Inter-VLAN Route</span>
                <span class="badge badge-blue">Layer 3</span>
            </div>
            <div style="font-size:0.85rem; color:#A3A3A3; margin-bottom:16px; line-height:1.5;">
                VLAN 30 devices isolated. Subinterface missing from Router-on-a-Stick config.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with preset_col3:
    st.markdown(
        """
        <div class="netsage-card" style="height:200px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="font-weight:800; color:#E5E5E5; font-family:'Outfit',sans-serif;">CASE-012 · Trunk Mode Misconfig</span>
                <span class="badge badge-purple">Layer 2</span>
            </div>
            <div style="font-size:0.85rem; color:#A3A3A3; margin-bottom:16px; line-height:1.5;">
                Switch inter-link configured as access port instead of 802.1Q trunk.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Quick Navigation Launchers
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🚀 Launch Platform Modules")

bcol1, bcol2, bcol3, bcol4 = st.columns(4)

with bcol1:
    st.page_link("pages/1_AI_Diagnosis.py", label="🔍 AI Diagnosis Console", use_container_width=True)
with bcol2:
    st.page_link("pages/2_Human_Review.py", label="👤 Human Review Queue", use_container_width=True)
with bcol3:
    st.page_link("pages/3_Dashboard.py", label="📊 Analytics Dashboard", use_container_width=True)
with bcol4:
    st.page_link("pages/4_Dataset_Manager.py", label="📁 Dataset Operations", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Covered Protocols Grid
st.markdown("### 🛡️ Enterprise Protocol Coverage")
concepts = [
    "VLAN Trunking", "DHCP Relay", "DNS Resolution", "ACL Rule Matrix", "OSPF Area 0",
    "Static Routing", "NAT Overload", "Port Security", "Inter-VLAN (RoAS)",
    "Subnet Masking", "Gateway Mismatches", "Interface Shutdown", "Duplicate IP Detection"
]
badges_html = "".join([f'<span class="badge badge-blue" style="margin:5px;">{c}</span>' for c in concepts])
st.markdown(f'<div class="netsage-card">{badges_html}</div>', unsafe_allow_html=True)
