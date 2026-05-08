"""
MatRisk AI - Settings Page
Application configuration and system diagnostics.
"""

import streamlit as st
import pandas as pd
import os
import sys
from utils.data_loader import get_dataset_summary
from utils.validation import perform_system_check
from utils.helpers import section_header, metric_card
from utils.constants import APP_NAME, APP_VERSION, DATASET_DIR


def render():
    """Render the Settings page."""
    st.markdown("# ⚙️ Settings & Diagnostics")
    st.markdown("System configuration, dataset validation, and platform diagnostics.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📦 Datasets", "🛡️ System Check", "ℹ️ About"])

    with tab1:
        section_header("Dataset Validation", "📦")

        summary = get_dataset_summary()

        rows = []
        for name, info in summary.items():
            rows.append({
                "Dataset": name,
                "Status": info["status"],
                "Rows": info["rows"],
                "Columns": info["columns"],
                "File Exists": "✅" if info["file_exists"] else "❌",
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption("📂 Storage: `datasets/processed/` — *Institutional Data Node Connected*")


        if st.button("🔄 Refresh Cache", key="refresh"):
            st.cache_data.clear()
            st.success("Cache cleared! Data will reload on next access.")
            st.rerun()

    with tab2:
        section_header("System Integrity Check", "🛡️")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("🚀 Run Comprehensive Check", key="run_check"):
                with st.spinner("Validating all schemas..."):
                    st.session_state.last_check = perform_system_check()
        
        with col2:
            st.caption("Validates core CSV schemas against production constants.")

        if "last_check" in st.session_state:
            report = st.session_state.last_check
            for name, result in report.items():
                status = "✅ PASS" if result.get("valid") else "❌ FAIL"
                with st.expander(f"{status} - {name.replace('_', ' ').title()}"):
                    if result.get("valid"):
                        st.success(f"Schema is valid. {len(result.get('unexpected', []))} additional columns found.")
                    else:
                        st.error(f"Missing Columns: {', '.join(result.get('missing', []))}")
                    
                    if result.get("unexpected"):
                        st.caption(f"Note: Unexpected columns found: {', '.join(result.get('unexpected', []))}")

    with tab3:
        section_header("Platform Diagnostics", "ℹ️")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📡 Session Info")
            st.json({
                "Session ID": st.session_state.get("session_id", "N/A"),
                "Current Page": st.session_state.get("current_page", "Home"),
                "Active Reports": len(st.session_state.get("generated_reports", [])),
                "Data Initialized": st.session_state.get("data_initialized", False)
            })

        with col2:
            st.markdown("### 🏗️ Versioning")
            st.markdown(f"""
            - **App Version:** {APP_VERSION}
            - **Python Version:** {sys.version.split()[0]}
            - **Streamlit Version:** {st.__version__}
            """)

        st.markdown("---")
        st.markdown("### 📝 About MatRisk AI")
        st.markdown(f"""
        {APP_NAME} is an enterprise-grade material intelligence and financial risk modelling platform. 
        It leverages advanced machine learning to bridge the gap between physical material properties 
        and institutional risk exposure.
        
        **© 2026 ZeTheta Advanced Agentic Coding Team**
        """)

        st.markdown("---")

        st.markdown("### 📊 Core Modules")
        st.markdown("""
        - 🧪 Material Intelligence — Property analysis & ML predictions
        - 🏗️ Infrastructure Risk — Asset monitoring & failure prediction
        - 📈 Commodity Analytics — Price tracking & trend analysis
        - 🌱 ESG Sustainability — Environmental impact & compliance
        - 🎮 MatRisk Lab — Simulations & stress testing
        - 🤖 AI Insights — Cross-domain intelligence

        ---

        **Tech Stack:**
        - Streamlit · Pandas · NumPy · Scikit-learn · Altair
        """)

        st.markdown("### 🛠️ Runtime Environment")
        try:
            # Using global sys imported at top
            sys_info = {
                "Python": sys.version.split()[0],
                "Streamlit": st.__version__,
                "Pandas": pd.__version__,
            }
            try:
                import numpy as np
                sys_info["NumPy"] = np.__version__
            except ImportError: pass
            
            try:
                import sklearn
                sys_info["Scikit-learn"] = sklearn.__version__
            except ImportError: pass
            
            try:
                import altair
                sys_info["Altair"] = altair.__version__
            except ImportError: pass

            info_df = pd.DataFrame(list(sys_info.items()), columns=["Package", "Version"])
            st.dataframe(info_df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.warning(f"Unable to retrieve full system info: {e}")

