"""
2_Human_Review.py – Human Review & Quality Assurance Board for NetSage AI Enterprise.

Enforces strict Responsible AI guardrails. Senior network engineers inspect, edit,
accept, or reject AI-generated telemetry diagnoses before logging and deployment.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from datetime import datetime

from modules.csv_manager import load_reviews, add_review, get_review_stats
from modules.utils import (
    generate_review_id, get_timestamp, confidence_to_label,
    osi_color, severity_color, normalise_osi_layer,
)
from modules.diagnosis import format_fix_steps_for_display as format_fix_steps
from modules import logger as app_logger

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Human Review Board – NetSage AI Enterprise",
    page_icon="👤",
    layout="wide",
)

# Master CSS import
from app import GLOBAL_CSS
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
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
if "pending_review" not in st.session_state:
    st.session_state.pending_review = []
if "review_submitted" not in st.session_state:
    st.session_state.review_submitted = []

# ---------------------------------------------------------------------------
# Header & Metrics Bar
# ---------------------------------------------------------------------------
st.markdown("""
<div class="fade-up" style="padding:32px 0 20px;">
    <div class="hero-eyebrow">◈ Human Review Board</div>
    <div class="hero-title">Human-in-the-Loop <span>Review</span> Board</div>
    <div class="hero-desc">Responsible AI Governance: Zero autonomous AI diagnosis is deployed without verified engineer oversight.</div>
</div>
""", unsafe_allow_html=True)

stats = get_review_stats()
s1, s2, s3, s4, s5 = st.columns(5)
with s1:
    st.metric("📥 Pending Queue", len(st.session_state.pending_review))
with s2:
    st.metric("✅ Verified Accepted", stats["accepted"])
with s3:
    st.metric("✏️ Human Corrected", stats["edited"])
with s4:
    st.metric("❌ Rejected Faults", stats["rejected"])
with s5:
    st.metric("🤖 Neural Precision", f"{stats['ai_agreement_pct']:.1f}%")

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Pending Reviews Queue
# ---------------------------------------------------------------------------
pending = st.session_state.pending_review
submitted_ids = {r.case_id for r in st.session_state.review_submitted}
pending_unreviewed = [r for r in pending if r.case_id not in submitted_ids]

if not pending_unreviewed:
    st.markdown(
        """
        <div class="netsage-card" style="text-align:center; padding:48px 24px;">
            <div style="font-size:3rem; margin-bottom:12px;">🎉</div>
            <div style="font-family:'Outfit',sans-serif; font-size:1.4rem; font-weight:700; color:#38BDF8; margin-bottom:6px;">
                Review Queue Clear
            </div>
            <div style="color:#9CA3AF; font-size:0.9rem; margin-bottom:20px;">
                All AI diagnoses have been reviewed. Run a new diagnostic analysis to send results to the review board.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_AI_Diagnosis.py", label="🔍 Launch AI Diagnostic Console", use_container_width=False)
else:
    st.markdown(
        f'<div style="color:#38BDF8; font-weight:700; margin-bottom:16px;">'
        f'📋 Awaiting Verification: <strong>{len(pending_unreviewed)}</strong> Incident Diagnosis(es)</div>',
        unsafe_allow_html=True,
    )

    for idx, diag_result in enumerate(pending_unreviewed):
        ai = diag_result.ai_response
        if ai is None:
            st.warning(f"Case {diag_result.case_id}: AI diagnosis failed – cannot review.")
            continue

        conf_int = ai.confidence_int()
        conf_label, conf_color = confidence_to_label(conf_int)
        osi_col_hex = osi_color(ai.osi_layer)

        with st.expander(
            f"🔍 Incident {diag_result.case_id} — {diag_result.symptom[:70]}…",
            expanded=(idx == 0),
        ):
            st.markdown("#### 🤖 AI-Generated Synthesis")

            r_col1, r_col2 = st.columns([3, 1])
            with r_col1:
                st.markdown(
                    f"""
                    <div class="netsage-card" style="padding:16px;">
                        <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em; color:#9CA3AF; margin-bottom:4px;">
                            AI Root Cause Diagnosis
                        </div>
                        <div style="font-size:1.05rem; font-weight:700; color:#F3F4F6;">{ai.root_cause}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with r_col2:
                st.markdown(
                    f"""
                    <div style="margin-top:6px;">
                        <span style="background:{osi_col_hex}25; color:{osi_col_hex}; border:1px solid {osi_col_hex}55; padding:4px 12px; border-radius:14px; font-size:0.8rem; font-weight:700;">
                            {ai.osi_layer}
                        </span>
                        <div style="margin-top:8px; font-size:0.8rem; color:{conf_color}; font-weight:700;">
                            Confidence: {conf_int}% ({conf_label})
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with st.expander("🔬 View Telemetry Evidence"):
                st.markdown(f'<div style="color:#D1D5DB; font-size:0.9rem;">{ai.evidence}</div>', unsafe_allow_html=True)

            st.markdown("**Proposed Remediation Commands:**")
            steps = format_fix_steps(ai.fix_steps)
            for si, step in enumerate(steps, 1):
                st.markdown(
                    f"""
                    <div class="terminal-window" style="margin:4px 0;">
                        <div class="terminal-body" style="padding:10px 14px; color:#F3F4F6; font-size:0.82rem;">
                            Step {si}: {step}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            # ── Reviewer Verification Form ─────────────────────────────────
            st.markdown("#### ✍️ Engineer Review Decision & Corrections")

            with st.form(key=f"review_form_{diag_result.case_id}_{idx}"):
                reviewer_name = st.text_input(
                    "👤 Senior Network Engineer Name",
                    value="Senior Network Engineer",
                    key=f"reviewer_{idx}",
                )

                review_action = st.radio(
                    "📋 Verification Decision",
                    options=["✅ Accept AI Diagnosis", "✏️ Edit & Correct Diagnosis", "❌ Reject Diagnosis"],
                    horizontal=True,
                    key=f"action_{idx}",
                )

                show_edit_fields = "Edit" in review_action

                human_root_cause = st.text_area(
                    "📝 Corrected Root Cause (if editing)",
                    value=ai.root_cause,
                    height=80,
                    disabled=not show_edit_fields,
                    key=f"hrc_{idx}",
                )

                h_col1, h_col2 = st.columns(2)
                with h_col1:
                    human_osi = st.selectbox(
                        "📶 Corrected OSI Layer",
                        options=[
                            "Layer 1 – Physical",
                            "Layer 2 – Data Link",
                            "Layer 3 – Network",
                            "Layer 4 – Transport",
                            "Layer 7 – Application",
                        ],
                        index=max(0, [
                            "Layer 1 – Physical", "Layer 2 – Data Link",
                            "Layer 3 – Network", "Layer 4 – Transport",
                            "Layer 7 – Application",
                        ].index(ai.osi_layer) if ai.osi_layer in [
                            "Layer 1 – Physical", "Layer 2 – Data Link",
                            "Layer 3 – Network", "Layer 4 – Transport",
                            "Layer 7 – Application",
                        ] else 0),
                        disabled=not show_edit_fields,
                        key=f"hosi_{idx}",
                    )
                with h_col2:
                    human_confidence = st.slider(
                        "🎯 Engineer Confidence Adjustment",
                        min_value=0,
                        max_value=100,
                        value=conf_int,
                        disabled=not show_edit_fields,
                        key=f"hconf_{idx}",
                    )

                human_fix_steps = st.text_area(
                    "🔧 Corrected Remediation Commands",
                    value=ai.fix_steps,
                    height=90,
                    disabled=not show_edit_fields,
                    key=f"hfix_{idx}",
                )

                reviewer_comments = st.text_area(
                    "💬 Governance & Review Audit Notes",
                    placeholder="Add operational comments regarding this decision...",
                    height=70,
                    key=f"comments_{idx}",
                )

                submit_review = st.form_submit_button(
                    "💾 Save & Commit Review Decision",
                    use_container_width=True,
                    type="primary",
                )

            if submit_review:
                if "Accept" in review_action:
                    status = "Accepted"
                elif "Edit" in review_action:
                    status = "Edited"
                else:
                    status = "Rejected"

                review_id = generate_review_id()
                review_row = {
                    "review_id": review_id,
                    "case_id": diag_result.case_id,
                    "original_symptom": diag_result.symptom,
                    "ai_root_cause": ai.root_cause,
                    "ai_osi_layer": ai.osi_layer,
                    "ai_confidence": str(conf_int),
                    "ai_fix_steps": ai.fix_steps,
                    "human_root_cause": human_root_cause if show_edit_fields else ai.root_cause,
                    "human_osi_layer": human_osi if show_edit_fields else ai.osi_layer,
                    "human_fix_steps": human_fix_steps if show_edit_fields else ai.fix_steps,
                    "human_evidence": ai.evidence,
                    "status": status,
                    "reviewer_comments": reviewer_comments,
                    "reviewer_name": reviewer_name,
                    "timestamp": get_timestamp(),
                }

                try:
                    add_review(review_row)
                    app_logger.log_human_review(
                        review_id, diag_result.case_id, status, reviewer_name, reviewer_comments
                    )
                    st.session_state.review_submitted.append(diag_result)
                    st.success(f"✅ Review decision '{status}' recorded! (Review ID: {review_id})")
                    st.rerun()

                except Exception as exc:
                    st.error(f"❌ Save failed: {exc}")

# ---------------------------------------------------------------------------
# Public Review Log Table
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("### 📜 Audit Log & Continuous Learning Trail")

reviews_df = load_reviews()
if reviews_df.empty:
    st.info("No reviews committed yet. Complete a diagnostic run to populate the review audit log.")
else:
    search_term = st.text_input("🔍 Search Audit Trail", placeholder="Filter by Case ID, Reviewer, or Status...")

    display_df = reviews_df.copy()
    if search_term:
        mask = display_df.apply(lambda row: search_term.lower() in row.to_string().lower(), axis=1)
        display_df = display_df[mask]

    st.markdown(f"**Showing {len(display_df)} committed review record(s)**")

    st.dataframe(
        display_df[["review_id", "case_id", "status", "reviewer_name", "ai_root_cause", "timestamp"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "review_id": "Review ID",
            "case_id": "Case ID",
            "status": st.column_config.TextColumn("Verdict"),
            "reviewer_name": "Engineer",
            "ai_root_cause": st.column_config.TextColumn("AI Diagnosis", width="large"),
            "timestamp": "Timestamp",
        },
    )

    # Corrected AI Examples Section
    edited_reviews = reviews_df[reviews_df["status"] == "Edited"]
    if not edited_reviews.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🧑‍🔬 Responsible AI: Corrected AI Diagnoses")
        st.markdown("Audit trail of instances where senior network engineers corrected the AI diagnosis:")

        for _, row in edited_reviews.head(5).iterrows():
            with st.expander(f"📋 Case {row['case_id']} — Reviewed by {row.get('reviewer_name', 'Engineer')}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**🤖 AI Original Diagnosis:**")
                    st.markdown(
                        f"""
                        <div style="background:rgba(239,68,68,0.1); border-left:3px solid #EF4444; padding:12px; border-radius:0 8px 8px 0; color:#F3F4F6; font-size:0.88rem;">
                            {row.get("ai_root_cause","—")}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c2:
                    st.markdown("**✅ Human Engineer Correction:**")
                    st.markdown(
                        f"""
                        <div style="background:rgba(16,185,129,0.1); border-left:3px solid #10B981; padding:12px; border-radius:0 8px 8px 0; color:#F3F4F6; font-size:0.88rem;">
                            {row.get("human_root_cause","—")}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                if row.get("reviewer_comments"):
                    st.caption(f"💬 Audit Note: {row['reviewer_comments']}")
