"""
4_Dataset_Manager.py – Dataset Manager for NetSage AI.

Features:
  - View the cases dataset with search/filter
  - Upload CSV to import new cases
  - Download CSV
  - Add new cases via form
  - Edit existing rows
  - Delete rows
  - Validate dataset integrity
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from modules.csv_manager import (
    load_cases, save_cases, add_case, delete_case, update_case,
    cases_to_csv_bytes, reviews_to_csv_bytes, validate_cases_df,
    import_cases_from_upload, CASES_COLUMNS,
)
from modules.utils import generate_case_id, get_timestamp
from modules import logger as app_logger

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dataset Manager – NetSage AI",
    page_icon="📁",
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
                Dataset Operations Portal
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

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown(
    '<h1 style="color:#58A6FF;font-weight:800;font-size:2.2rem">📁 Dataset Manager</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="color:#8B949E;margin-bottom:1.5rem">Manage the cases dataset: view, search, add, edit, delete, upload, download, and validate.</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_view, tab_add, tab_edit, tab_delete, tab_upload, tab_validate = st.tabs([
    "📋 View Dataset",
    "➕ Add Case",
    "✏️ Edit Row",
    "🗑️ Delete Row",
    "⬆️ Upload CSV",
    "✅ Validate",
])

# ============================================================================
# Tab 1: View Dataset
# ============================================================================
with tab_view:
    st.markdown("### 📋 Cases Dataset")
    cases_df = load_cases()

    # Stats
    v1, v2, v3 = st.columns(3)
    with v1:
        st.metric("Total Cases", len(cases_df))
    with v2:
        st.metric("Unique Concepts", cases_df["concept_tag"].nunique() if not cases_df.empty else 0)
    with v3:
        st.metric("OSI Layers", cases_df["osi_layer"].nunique() if not cases_df.empty else 0)

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        search = st.text_input("🔍 Search", placeholder="Search all columns…")
    with col_f2:
        if not cases_df.empty and "osi_layer" in cases_df.columns:
            osi_filter = st.selectbox("Filter by OSI Layer", ["All"] + sorted(cases_df["osi_layer"].unique().tolist()))
        else:
            osi_filter = "All"
    with col_f3:
        if not cases_df.empty and "severity" in cases_df.columns:
            sev_filter = st.selectbox("Filter by Severity", ["All"] + sorted(cases_df["severity"].unique().tolist()))
        else:
            sev_filter = "All"

    filtered = cases_df.copy()
    if search:
        mask = filtered.apply(lambda row: search.lower() in row.to_string().lower(), axis=1)
        filtered = filtered[mask]
    if osi_filter != "All" and "osi_layer" in filtered.columns:
        filtered = filtered[filtered["osi_layer"] == osi_filter]
    if sev_filter != "All" and "severity" in filtered.columns:
        filtered = filtered[filtered["severity"] == sev_filter]

    st.markdown(f"**Showing {len(filtered)} of {len(cases_df)} cases**")

    if not filtered.empty:
        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
            column_config={
                "case_id": st.column_config.TextColumn("Case ID", width="small"),
                "symptom": st.column_config.TextColumn("Symptom", width="large"),
                "osi_layer": st.column_config.TextColumn("OSI Layer", width="medium"),
                "concept_tag": st.column_config.TextColumn("Concept", width="medium"),
                "severity": st.column_config.TextColumn("Severity", width="small"),
                "show_output": st.column_config.TextColumn("Show Output", width="large"),
            },
        )

    # Download buttons
    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            "⬇️ Download cases.csv",
            data=cases_to_csv_bytes(),
            file_name="cases.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with dl_col2:
        st.download_button(
            "⬇️ Download review_log.csv",
            data=reviews_to_csv_bytes(),
            file_name="human_review_log.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ============================================================================
# Tab 2: Add New Case
# ============================================================================
with tab_add:
    st.markdown("### ➕ Add New Case")
    st.markdown("Fill in all required fields to add a new troubleshooting case to the dataset.")

    with st.form("add_case_form"):
        a1, a2 = st.columns(2)
        with a1:
            new_case_id = st.text_input(
                "Case ID *",
                value=generate_case_id(),
                help="Unique identifier for this case",
            )
            new_symptom = st.text_area("Symptom *", height=80, placeholder="Describe the observed network problem…")
            new_topology = st.text_area("Topology Note", height=70, placeholder="Describe the network layout…")
            new_severity = st.selectbox("Severity *", ["High", "Medium", "Low", "Critical", "Info"])
        with a2:
            new_osi = st.selectbox("OSI Layer *", [
                "Layer 1 – Physical", "Layer 2 – Data Link", "Layer 3 – Network",
                "Layer 4 – Transport", "Layer 7 – Application",
            ])
            new_concept = st.text_input("Concept Tag *", placeholder="e.g., VLAN, DHCP, OSPF…")
            new_expected = st.text_area("Expected Fault *", height=70, placeholder="Describe the expected root cause…")
            new_answer = st.text_area("Correct Answer *", height=80, placeholder="Step-by-step correct fix…")

        new_show = st.text_area(
            "Show Output",
            height=130,
            placeholder="Paste Cisco show command output…",
        )

        add_submitted = st.form_submit_button("➕ Add Case", type="primary", use_container_width=True)

    if add_submitted:
        errors = []
        if not new_case_id.strip(): errors.append("Case ID is required")
        if not new_symptom.strip(): errors.append("Symptom is required")
        if not new_expected.strip(): errors.append("Expected Fault is required")
        if not new_answer.strip(): errors.append("Correct Answer is required")
        if not new_concept.strip(): errors.append("Concept Tag is required")

        if errors:
            for err in errors:
                st.error(f"❌ {err}")
        else:
            # Check for duplicate case_id
            existing = load_cases()
            if new_case_id in existing["case_id"].values:
                st.error(f"❌ Case ID '{new_case_id}' already exists. Use a unique ID.")
            else:
                try:
                    add_case({
                        "case_id": new_case_id,
                        "symptom": new_symptom,
                        "topology_note": new_topology,
                        "show_output": new_show,
                        "expected_fault": new_expected,
                        "osi_layer": new_osi,
                        "concept_tag": new_concept,
                        "severity": new_severity,
                        "correct_answer": new_answer,
                    })
                    app_logger.log_csv_operation("ADD_CASE", "cases.csv", 1)
                    st.success(f"✅ Case '{new_case_id}' added successfully!")
                    st.rerun()
                except Exception as exc:
                    st.error(f"❌ Failed to add case: {exc}")

# ============================================================================
# Tab 3: Edit Row
# ============================================================================
with tab_edit:
    st.markdown("### ✏️ Edit Existing Case")
    cases_df = load_cases()

    if cases_df.empty:
        st.info("No cases to edit.")
    else:
        case_ids = cases_df["case_id"].tolist()
        selected_id = st.selectbox("Select Case to Edit", case_ids)

        selected_row = cases_df[cases_df["case_id"] == selected_id].iloc[0]

        with st.form("edit_case_form"):
            e1, e2 = st.columns(2)
            with e1:
                ed_symptom = st.text_area("Symptom", value=selected_row.get("symptom", ""), height=80)
                ed_topology = st.text_area("Topology Note", value=selected_row.get("topology_note", ""), height=70)
                ed_severity = st.selectbox(
                    "Severity",
                    ["High", "Medium", "Low", "Critical", "Info"],
                    index=["High", "Medium", "Low", "Critical", "Info"].index(
                        selected_row.get("severity", "Medium")
                    ) if selected_row.get("severity", "Medium") in ["High", "Medium", "Low", "Critical", "Info"] else 0,
                )
            with e2:
                osi_options = [
                    "Layer 1 – Physical", "Layer 2 – Data Link", "Layer 3 – Network",
                    "Layer 4 – Transport", "Layer 7 – Application",
                ]
                ed_osi = st.selectbox(
                    "OSI Layer",
                    osi_options,
                    index=osi_options.index(selected_row.get("osi_layer", "Layer 3 – Network"))
                    if selected_row.get("osi_layer", "") in osi_options else 2,
                )
                ed_concept = st.text_input("Concept Tag", value=selected_row.get("concept_tag", ""))
                ed_expected = st.text_area("Expected Fault", value=selected_row.get("expected_fault", ""), height=70)
                ed_answer = st.text_area("Correct Answer", value=selected_row.get("correct_answer", ""), height=70)

            ed_show = st.text_area("Show Output", value=selected_row.get("show_output", ""), height=120)

            edit_submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)

        if edit_submitted:
            try:
                update_case(selected_id, {
                    "symptom": ed_symptom,
                    "topology_note": ed_topology,
                    "show_output": ed_show,
                    "expected_fault": ed_expected,
                    "osi_layer": ed_osi,
                    "concept_tag": ed_concept,
                    "severity": ed_severity,
                    "correct_answer": ed_answer,
                })
                app_logger.log_csv_operation("EDIT_CASE", "cases.csv", 1)
                st.success(f"✅ Case '{selected_id}' updated successfully!")
                st.rerun()
            except Exception as exc:
                st.error(f"❌ Edit failed: {exc}")

# ============================================================================
# Tab 4: Delete Row
# ============================================================================
with tab_delete:
    st.markdown("### 🗑️ Delete Case")
    st.warning("⚠️ Deletion is permanent and cannot be undone.")

    cases_df = load_cases()

    if cases_df.empty:
        st.info("No cases to delete.")
    else:
        del_id = st.selectbox("Select Case to Delete", cases_df["case_id"].tolist(), key="delete_select")

        # Preview
        preview = cases_df[cases_df["case_id"] == del_id]
        if not preview.empty:
            st.markdown(f"**Symptom:** {preview.iloc[0].get('symptom','')[:100]}")
            st.markdown(f"**Concept:** {preview.iloc[0].get('concept_tag','')}")

        col_del1, col_del2 = st.columns(2)
        with col_del1:
            confirm = st.checkbox("I confirm I want to delete this case permanently")
        with col_del2:
            if st.button("🗑️ Delete Case", type="primary") and confirm:
                if delete_case(del_id):
                    app_logger.log_csv_operation("DELETE_CASE", "cases.csv", 1)
                    st.success(f"✅ Case '{del_id}' deleted.")
                    st.rerun()
                else:
                    st.error("❌ Case not found.")
            elif not confirm:
                st.caption("Check the confirmation box to enable deletion.")

# ============================================================================
# Tab 5: Upload CSV
# ============================================================================
with tab_upload:
    st.markdown("### ⬆️ Upload Cases CSV")
    st.markdown(
        "Upload a CSV file with the same column structure as `cases.csv`. "
        "New rows will be merged with existing data (duplicates by `case_id` are kept, "
        "latest version wins)."
    )

    st.markdown("**Required columns:**")
    st.code(", ".join(CASES_COLUMNS))

    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded:
        success, message, count = import_cases_from_upload(uploaded)
        if success:
            app_logger.log_csv_operation("UPLOAD_CSV", "cases.csv", count)
            st.success(f"✅ {message} Imported **{count}** rows.")
            st.rerun()
        else:
            st.error(f"❌ {message}")

    st.markdown("---")
    st.markdown("#### 📋 CSV Template")
    template_df = pd.DataFrame(columns=CASES_COLUMNS)
    st.download_button(
        "⬇️ Download Empty Template",
        data=template_df.to_csv(index=False).encode("utf-8"),
        file_name="cases_template.csv",
        mime="text/csv",
    )

# ============================================================================
# Tab 6: Validate
# ============================================================================
with tab_validate:
    st.markdown("### ✅ Dataset Validation")
    st.markdown("Run integrity checks on the cases dataset to find schema errors, duplicates, and missing data.")

    cases_df = load_cases()

    if st.button("🔍 Run Validation", type="primary"):
        with st.spinner("Validating…"):
            errors = validate_cases_df(cases_df)

        if not errors:
            st.success(f"✅ Dataset is valid! {len(cases_df)} rows, no issues found.")
            st.balloons()
        else:
            st.error(f"❌ Found {len(errors)} validation issue(s):")
            for err in errors:
                st.markdown(f"- 🔴 {err}")

        # Stats
        st.markdown("#### Dataset Summary")
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric("Total Rows", len(cases_df))
        with s2:
            st.metric("Unique Case IDs", cases_df["case_id"].nunique())
        with s3:
            st.metric("Empty Symptoms", len(cases_df[cases_df["symptom"].str.strip() == ""]))
        with s4:
            st.metric("Duplicate IDs", len(cases_df[cases_df.duplicated(subset=["case_id"])]))

        # Column completeness
        st.markdown("#### Column Completeness")
        completeness = {
            col: f"{(cases_df[col].str.strip().ne('').sum() / len(cases_df) * 100):.1f}%"
            if len(cases_df) > 0 else "N/A"
            for col in CASES_COLUMNS
            if col in cases_df.columns
        }
        comp_df = pd.DataFrame(list(completeness.items()), columns=["Column", "Completeness"])
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
