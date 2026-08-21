"""
1_AI_Diagnosis.py – AI Autonomous Diagnosis Module for NetSage AI.

Ingests CLI output & network symptom reports, executes deterministic rule evaluation,
runs Gemini neural diagnostic model, and renders structured root cause & CLI playbook.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import streamlit as st

from modules.diagnosis import run_diagnosis, format_fix_steps_for_display
from modules.ai_engine import is_api_key_configured
from modules.csv_manager import load_cases
from modules.utils import (
    generate_case_id, get_timestamp, confidence_to_label,
    osi_color, severity_color, truncate_text,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Diagnosis Console – NetSage AI Enterprise",
    page_icon="🔍",
    layout="wide",
)

# Master CSS import from app.py
from app import GLOBAL_CSS
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar nav & status
# ---------------------------------------------------------------------------
with st.sidebar:
    from modules.ai_engine import is_api_key_configured
    api_ok = is_api_key_configured()
    st.markdown("""
<div style="padding:20px 8px 16px; border-bottom:1px solid rgba(255,255,255,0.07); margin-bottom:16px;">
    <div style="display:flex; align-items:center; gap:10px;">
        <div style="width:36px; height:36px; border-radius:9px; flex-shrink:0; background:linear-gradient(135deg, #3B82F6 0%, #10B981 100%); display:flex; align-items:center; justify-content:center; font-size:1.1rem; box-shadow:0 4px 12px rgba(59,130,246,0.4);">🛰️</div>
        <div>
            <div style="font-family:'Space Grotesk',sans-serif; font-size:1.05rem; font-weight:800; color:#F1F5F9; letter-spacing:-0.02em;">NetSage AI</div>
            <div style="font-size:0.68rem; color:#475569; font-weight:500; letter-spacing:0.04em; text-transform:uppercase;">Enterprise v2.5</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    if api_ok:
        st.markdown("""
<div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.2); border-radius:10px; padding:10px 14px; margin-bottom:18px;">
    <div style="display:flex; align-items:center; gap:8px;">
        <span class="status-dot status-online"></span>
        <span style="font-size:0.82rem; font-weight:600; color:#34D399;">Gemini AI Online</span>
    </div>
    <div style="font-size:0.72rem; color:#475569; margin-top:3px; padding-left:16px;">gemini-3.6-flash • Connected</div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.2); border-radius:10px; padding:10px 14px; margin-bottom:18px;">
    <div style="display:flex; align-items:center; gap:8px;">
        <span class="status-dot status-warning"></span>
        <span style="font-size:0.82rem; font-weight:600; color:#FCD34D;">Offline Mode</span>
    </div>
    <div style="font-size:0.72rem; color:#475569; margin-top:3px; padding-left:16px;">Rule Engine Active • No API Key</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.09em; color:#334155; margin-bottom:6px;">Navigation</div>', unsafe_allow_html=True)
    st.page_link("app.py",                       label="⌂  Command Center",       use_container_width=True)
    st.page_link("pages/1_AI_Diagnosis.py",       label="◎  AI Diagnosis",         use_container_width=True)
    st.page_link("pages/2_Human_Review.py",       label="◈  Human Review Board",   use_container_width=True)
    st.page_link("pages/3_Dashboard.py",          label="▦  Analytics Dashboard",  use_container_width=True)
    st.page_link("pages/4_Dataset_Manager.py",    label="⊞  Dataset Manager",      use_container_width=True)
    st.page_link("pages/5_About.py",              label="◉  Architecture & Docs",  use_container_width=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "diagnosis_history" not in st.session_state:
    st.session_state.diagnosis_history = []
if "current_diagnosis" not in st.session_state:
    st.session_state.current_diagnosis = None
if "pending_review" not in st.session_state:
    st.session_state.pending_review = []

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="fade-up" style="padding:32px 0 20px;">
    <div class="hero-eyebrow">◎ AI Diagnosis Console</div>
    <div class="hero-title">Autonomous <span>Diagnosis</span> Engine</div>
    <div class="hero-desc">Execute dual-stage analysis: 14-Rule Deterministic Evaluation + Gemini Neural OSI Synthesis.</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Quick Case Preset Picker
# ---------------------------------------------------------------------------
cases_df = load_cases()
case_options = ["— Select Quick-Fill Preset or Enter Custom Case —"] + [
    f"{row['case_id']} · {row['concept_tag']} · {row['symptom'][:50]}…" for _, row in cases_df.iterrows()
]

st.markdown("### 📋 Telemetry & Incident Input")

preset_selection = st.selectbox(
    "🧪 Quick Load Test Scenario from Knowledge Base",
    options=case_options,
    index=0,
    help="Select a pre-configured Cisco Packet Tracer incident to auto-fill telemetry inputs",
)

default_symptom = ""
default_topology = ""
default_show = ""

if preset_selection != "— Select Quick-Fill Preset or Enter Custom Case —":
    cid_match = preset_selection.split(" · ")[0]
    matched_row = cases_df[cases_df["case_id"] == cid_match]
    if not matched_row.empty:
        r = matched_row.iloc[0]
        default_symptom = r.get("symptom", "")
        default_topology = r.get("topology_note", "")
        default_show = r.get("show_output", "")

with st.form("diagnosis_form", clear_on_submit=False):
    col_left, col_right = st.columns([1, 1])

    with col_left:
        symptom = st.text_area(
            "🔴 Reported Symptom & Anomaly Description *",
            value=default_symptom,
            height=140,
            placeholder="e.g. PC0 gets IP via DHCP but cannot ping Default Gateway 192.168.10.1.\nExternal web browsing fails across VLAN 10.",
            help="Describe the observed network issue clearly.",
        )
        topology = st.text_area(
            "🗺️ Lab Topology & Subnet Notes",
            value=default_topology,
            height=110,
            placeholder="e.g. PC0 (VLAN 10) -> Switch1 (Fa0/1) -> Router0 (Gi0/0.10 RoAS) -> ISP Router",
            help="Optional topology details to assist OSI layer mapping.",
        )

    with col_right:
        show_output = st.text_area(
            "💻 Cisco IOS 'show' Telemetry Output *",
            value=default_show,
            height=270,
            placeholder="Router0# show ip interface brief\nInterface              IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0.10 192.168.10.1    YES manual administratively down down\n\nRouter0# show ip route\n...",
            help="Paste CLI outputs like 'show ip int brief', 'show ip route', 'show vlan brief', 'show running-config'",
        )

    submitted = st.form_submit_button(
        "🚀 Execute Diagnostic Engine",
        use_container_width=True,
        type="primary",
    )

# ---------------------------------------------------------------------------
# Run Diagnosis Engine
# ---------------------------------------------------------------------------
if submitted:
    if not symptom.strip():
        st.error("❌ Symptom description is required to initiate diagnostic pipeline.")
        st.stop()
    if not show_output.strip():
        st.warning("⚠️ No CLI show command telemetry provided. Running in degraded heuristic mode.")

    cid = generate_case_id()

    with st.spinner("⚙️ Executing Stage 1: Deterministic 14-Rule Heuristic Check..."):
        import time; time.sleep(0.3)

    with st.spinner("🤖 Executing Stage 2: Gemini Neural Diagnostic Synthesis..."):
        result = run_diagnosis(
            symptom=symptom,
            topology=topology,
            show_output=show_output,
            case_id=cid,
        )

    st.session_state.current_diagnosis = result
    st.session_state.diagnosis_history.insert(0, result)
    st.session_state.pending_review.insert(0, result)
    st.success("✅ Diagnostic run complete! Synthesized findings rendered below.")

# ---------------------------------------------------------------------------
# Render Diagnostic Results
# ---------------------------------------------------------------------------
result = st.session_state.current_diagnosis

if result:
    st.markdown("---")
    st.markdown("## 📊 Autonomous Diagnostic Report")

    # Header Row
    sev_color = severity_color(result.overall_severity)
    h_col1, h_col2 = st.columns([3, 1])

    with h_col1:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
                <span style="font-weight:700; font-size:1.1rem; color:#F3F4F6;">Incident ID: <code style="color:#38BDF8">{result.case_id}</code></span>
                <span style="background:{sev_color}; color:#FFFFFF; padding:4px 14px; border-radius:20px; font-weight:700; font-size:0.8rem; letter-spacing:0.04em;">
                    SEVERITY: {result.overall_severity.upper()}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with h_col2:
        st.markdown(
            f'<div style="text-align:right; color:#9CA3AF; font-size:0.82rem;">⏱️ Timestamp: {result.timestamp}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stage 1: Deterministic Rule Matrix ──────────────────────────────────
    st.markdown("### ⚙️ Stage 1 · Heuristic Rule Matrix Evaluation")

    if result.rule_findings:
        summary = result.rule_summary
        r1, r2, r3 = st.columns(3)
        with r1:
            st.metric("🔴 High Severity Faults", summary.get("High", 0))
        with r2:
            st.metric("🟡 Medium Severity Anomlies", summary.get("Medium", 0))
        with r3:
            st.metric("🟢 Informational Flags", summary.get("Low", 0))

        for finding in result.rule_findings:
            sev = finding.get("severity", "Medium")
            border_color = severity_color(sev)
            st.markdown(
                f"""
                <div style="background:rgba(15, 23, 42, 0.7); border-left:4px solid {border_color}; border-radius:0 12px 12px 0; padding:14px 18px; margin:10px 0; border-top:1px solid rgba(255,255,255,0.05); border-right:1px solid rgba(255,255,255,0.05); border-bottom:1px solid rgba(255,255,255,0.05);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span style="font-weight:700; color:#F3F4F6; font-size:0.95rem;">{finding["issue"]}</span>
                        <span class="badge badge-rose">{sev} Severity</span>
                    </div>
                    <div style="color:#9CA3AF; font-size:0.82rem; margin-bottom:6px;">
                        <strong>Rule Trigger:</strong> <code>{finding["rule_name"]}</code>
                    </div>
                    <div style="color:#34D399; font-size:0.85rem; font-weight:600;">
                        💡 Recommendation: {finding["recommendation"]}
                    </div>
                    <div style="color:#6B7280; font-size:0.75rem; margin-top:6px; font-family:'JetBrains Mono',monospace;">
                        Evidence: {finding.get("matched_evidence","")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25); border-radius:12px; padding:14px 18px; color:#34D399; font-size:0.9rem;">
                ✅ <strong>Zero Heuristic Rule Violations Triggered.</strong> Proceeding to neural OSI synthesis.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stage 2: Gemini Neural AI Diagnosis ─────────────────────────────────
    st.markdown("### 🤖 Stage 2 · Neural OSI Diagnostic Synthesis (Gemini Engine)")

    if result.ai_error and not result.ai_response:
        st.error(f"❌ AI engine exception: {result.ai_error}")
    elif result.ai_response:
        ai = result.ai_response
        conf_int = ai.confidence_int()
        conf_label, conf_color = confidence_to_label(conf_int)
        osi_col_hex = osi_color(ai.osi_layer)

        # Primary Root Cause Card
        st.markdown(
            f"""
            <div class="netsage-card netsage-card-glow">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px; margin-bottom:18px;">
                    <div style="flex:1; min-width:280px;">
                        <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; color:#9CA3AF; font-weight:700; margin-bottom:6px;">
                            Identified Root Cause
                        </div>
                        <div style="font-size:1.15rem; font-weight:700; color:#F9FAFB; line-height:1.5;">
                            {ai.root_cause}
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:{osi_col_hex}25; color:{osi_col_hex}; border:1px solid {osi_col_hex}55; padding:6px 16px; border-radius:20px; font-size:0.85rem; font-weight:700; display:inline-block; margin-bottom:8px;">
                            {ai.osi_layer}
                        </span>
                        <div style="font-size:0.82rem; color:{conf_color}; font-weight:700;">
                            Confidence Score: {conf_int}% ({conf_label})
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(conf_int / 100)

        st.markdown("<br>", unsafe_allow_html=True)

        col_ev, col_fix = st.columns([1, 1])

        with col_ev:
            st.markdown("#### 🔬 Diagnostic Evidence Analysis")
            st.markdown(
                f"""
                <div class="netsage-card" style="min-height:180px;">
                    <div style="color:#D1D5DB; font-size:0.9rem; line-height:1.7;">
                        {ai.evidence}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("#### ⚡ Recommended Verification Command")
            st.markdown(
                f"""
                <div class="terminal-window">
                    <div class="terminal-header">
                        <span class="dot dot-red"></span>
                        <span class="dot dot-yellow"></span>
                        <span class="dot dot-green"></span>
                        <span class="terminal-title">Cisco IOS Verification CLI</span>
                    </div>
                    <div class="terminal-body">Router# {ai.next_command}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_fix:
            st.markdown("#### 🔧 Cisco IOS Remediation Playbook")
            steps = format_fix_steps_for_display(ai.fix_steps)
            if steps:
                for i, step in enumerate(steps, 1):
                    st.markdown(
                        f"""
                        <div class="terminal-window" style="margin:8px 0;">
                            <div class="terminal-header">
                                <span style="font-size:0.75rem; color:#38BDF8; font-weight:700;">Step {i}</span>
                            </div>
                            <div class="terminal-body" style="color:#F9FAFB; font-size:0.85rem;">{step}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    f"""
                    <div class="terminal-window">
                        <div class="terminal-body" style="color:#F9FAFB;">{ai.fix_steps}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ── Action Bar ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🎯 Actions & Guardrail Workflow")
    act_col1, act_col2, act_col3, act_col4 = st.columns(4)

    with act_col1:
        st.page_link("pages/2_Human_Review.py", label="👤 Submit to Human Review", use_container_width=True)

    with act_col2:
        if st.button("📋 Copy Case ID", use_container_width=True):
            st.toast(f"Copied Case ID: {result.case_id}", icon="📋")

    with act_col3:
        diag_json = json.dumps(result.to_dict(), indent=2, default=str)
        st.download_button(
            label="⬇️ Download Telemetry JSON",
            data=diag_json,
            file_name=f"{result.case_id}_telemetry.json",
            mime="application/json",
            use_container_width=True,
        )

    with act_col4:
        if st.button("🔄 New Diagnostic Run", use_container_width=True):
            st.session_state.current_diagnosis = None
            st.rerun()

# ---------------------------------------------------------------------------
# Diagnostic Session Log
# ---------------------------------------------------------------------------
if st.session_state.diagnosis_history:
    st.markdown("---")
    st.markdown("### 🕐 Session Diagnostic History")

    with st.expander(f"Inspect {len(st.session_state.diagnosis_history)} diagnostic runs from this session"):
        for hist in st.session_state.diagnosis_history:
            rc = truncate_text(hist.ai_response.root_cause, 90) if hist.ai_response else "No AI response"
            sev_c = severity_color(hist.overall_severity)
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.06);">
                    <div>
                        <span style="font-weight:700; color:#38BDF8; font-family:'JetBrains Mono',monospace;">{hist.case_id}</span>
                        <span style="color:#9CA3AF; font-size:0.85rem; margin-left:12px;">{rc}</span>
                    </div>
                    <span style="background:{sev_c}; color:#FFF; padding:2px 10px; border-radius:12px; font-size:0.72rem; font-weight:700;">
                        {hist.overall_severity}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
