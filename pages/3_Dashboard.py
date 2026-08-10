"""
3_Dashboard.py – Executive Analytics & Telemetry Dashboard for NetSage AI Enterprise.

Renders real-time Plotly charts, AI accuracy metrics, fault vectors, OSI layer distribution,
and Responsible AI audit metrics.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from modules.csv_manager import load_cases, load_reviews, get_review_stats
from modules.dashboard import (
    chart_issue_type_distribution,
    chart_osi_layer_distribution,
    chart_severity_distribution,
    chart_review_status,
    chart_confidence_histogram,
    chart_top_problems,
    chart_rule_findings,
    chart_review_timeline,
    chart_ai_accuracy_gauge,
)
from modules.utils import severity_color, osi_color

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Executive Analytics – NetSage AI Enterprise",
    page_icon="📊",
    layout="wide",
)

# Master CSS import
from app import GLOBAL_CSS
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown(
        """
        <div style="padding:10px 4px 16px; text-align:center;">
            <div style="font-size:2.2rem; margin-bottom:4px;">🌐</div>
            <div style="font-family:'Outfit',sans-serif; font-size:1.3rem; font-weight:800; background:linear-gradient(135deg, #38BDF8, #818CF8); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                NetSage AI
            </div>
            <div style="font-size:0.75rem; color:#6B7280; font-weight:500; margin-top:2px;">
                Executive Command Center
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.page_link("app.py", label="🏠 Command Center", use_container_width=True)
    st.page_link("pages/1_AI_Diagnosis.py", label="🔍 AI Diagnosis", use_container_width=True)
    st.page_link("pages/2_Human_Review.py", label="👤 Human Review Board", use_container_width=True)
    st.page_link("pages/3_Dashboard.py", label="📊 Analytics & Metrics", use_container_width=True)
    st.page_link("pages/4_Dataset_Manager.py", label="📁 Dataset Operations", use_container_width=True)
    st.page_link("pages/5_About.py", label="ℹ️ Architecture & Specs", use_container_width=True)

# Data load
cases_df = load_cases()
reviews_df = load_reviews()
stats = get_review_stats()

# Header
st.markdown(
    """
    <div style="margin-bottom:20px;">
        <h1 style="color:#F9FAFB; font-weight:800; font-size:2.2rem; margin-bottom:4px;">📊 Platform Analytics & Telemetry</h1>
        <p style="color:#9CA3AF; margin:0; font-size:0.95rem;">
            Real-time performance metrics, neural precision metrics, OSI fault vectors, and engineer review statistics.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# KPI Row
total_cases = len(cases_df)
total_reviews = stats["total"]
ai_accuracy = stats["ai_agreement_pct"]
most_common = (
    cases_df["concept_tag"].value_counts().index[0]
    if not cases_df.empty and "concept_tag" in cases_df.columns and len(cases_df) > 0
    else "N/A"
)
human_corrections = stats["edited"] + stats["rejected"]

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{total_cases}</div>'
        f'<div class="metric-label">📁 Knowledge Cases</div></div>',
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value">{total_reviews}</div>'
        f'<div class="metric-label">👤 Commited Reviews</div></div>',
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value" style="color:#34D399">{ai_accuracy:.1f}%</div>'
        f'<div class="metric-label">🤖 AI Agreement Rate</div></div>',
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value" style="color:#FBBF24">{human_corrections}</div>'
        f'<div class="metric-label">✏️ Engineer Fixes</div></div>',
        unsafe_allow_html=True,
    )
with k5:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value" style="font-size:1.3rem; color:#818CF8">{most_common}</div>'
        f'<div class="metric-label">🔝 Dominant Vector</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Charts Section
c1, c2 = st.columns([3, 2])

with c1:
    st.markdown('<div class="netsage-card">', unsafe_allow_html=True)
    fig1 = chart_issue_type_distribution(cases_df)
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="netsage-card">', unsafe_allow_html=True)
    fig2 = chart_osi_layer_distribution(cases_df)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

c3, c4, c5 = st.columns([2, 2, 1.5])

with c3:
    st.markdown('<div class="netsage-card">', unsafe_allow_html=True)
    fig3 = chart_severity_distribution(cases_df)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="netsage-card">', unsafe_allow_html=True)
    fig4 = chart_review_status(reviews_df)
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c5:
    st.markdown('<div class="netsage-card">', unsafe_allow_html=True)
    fig_gauge = chart_ai_accuracy_gauge(ai_accuracy)
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

c6, c7 = st.columns(2)

with c6:
    st.markdown('<div class="netsage-card">', unsafe_allow_html=True)
    fig5 = chart_confidence_histogram(reviews_df)
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c7:
    st.markdown('<div class="netsage-card">', unsafe_allow_html=True)
    fig8 = chart_review_timeline(reviews_df)
    st.plotly_chart(fig8, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="netsage-card">', unsafe_allow_html=True)
fig6 = chart_top_problems(cases_df)
st.plotly_chart(fig6, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Responsible AI Breakdown
st.markdown("---")
st.markdown("### 🛡️ Governance & Responsible AI Operational Metrics")

resp_col1, resp_col2, resp_col3 = st.columns(3)

with resp_col1:
    st.markdown(
        f"""
        <div class="netsage-card" style="text-align:center">
            <div style="font-size:2rem; margin-bottom:6px;">✅</div>
            <div style="font-size:2.2rem; font-weight:800; color:#34D399">{stats['accepted']}</div>
            <div style="color:#9CA3AF; font-size:0.85rem">Direct AI Acceptance</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with resp_col2:
    st.markdown(
        f"""
        <div class="netsage-card" style="text-align:center">
            <div style="font-size:2rem; margin-bottom:6px;">✏️</div>
            <div style="font-size:2.2rem; font-weight:800; color:#FBBF24">{stats['edited']}</div>
            <div style="color:#9CA3AF; font-size:0.85rem">Engineer Fine-Tuned Fixes</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with resp_col3:
    st.markdown(
        f"""
        <div class="netsage-card" style="text-align:center">
            <div style="font-size:2rem; margin-bottom:6px;">❌</div>
            <div style="font-size:2.2rem; font-weight:800; color:#FB7185">{stats['rejected']}</div>
            <div style="color:#9CA3AF; font-size:0.85rem">Hallucinated / Rejected Diagnoses</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.button("🔄 Refresh Analytics Feed"):
    st.rerun()
