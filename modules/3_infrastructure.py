"""
MatRisk AI - Infrastructure Analytics Page
Bridge and asset monitoring, risk scoring, and failure analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_infrastructure_assets, load_historical_failures, load_infrastructure
from utils.helpers import metric_card, section_header, empty_state, format_currency
from components.charts import bar_chart, scatter_chart, histogram_chart, donut_chart, line_chart
from services.risk_service import compute_infrastructure_risk, compute_financial_exposure, failure_probability_analysis


def render():
    """Render the Infrastructure Analytics page."""
    st.markdown("# 🏗️ Infrastructure Risk Analytics")
    st.markdown("Monitor assets, analyze risk, and plan maintenance interventions.")
    st.markdown("---")

    infra = load_infrastructure_assets()
    failures = load_historical_failures()
    fleet = load_infrastructure()

    if infra.empty and fleet.empty:
        empty_state("No infrastructure data loaded.")
        return

    # Compute risk scores
    infra_risk = compute_infrastructure_risk(infra)

    # ─── Filters ───────────────────────────────────────────────
    section_header("Filters", "🔍")

    col1, col2, col3, col4 = st.columns(4)

    params = st.session_state.infra_filters

    with col1:
        types = ["All"] + sorted(infra_risk["bridge_type"].dropna().unique().tolist()) if "bridge_type" in infra_risk.columns else ["All"]
        default_type = params.get("type", "All")
        if default_type not in types: default_type = "All"
        sel_type = st.selectbox("Asset Type", types, index=types.index(default_type), key="infra_type_sel")
        st.session_state.infra_filters["type"] = sel_type

    with col2:
        materials = ["All"] + sorted(infra_risk["material"].dropna().unique().tolist()) if "material" in infra_risk.columns else ["All"]
        default_mat = params.get("material", "All")
        if default_mat not in materials: default_mat = "All"
        sel_mat = st.selectbox("Material", materials, index=materials.index(default_mat), key="infra_mat_sel")
        st.session_state.infra_filters["material"] = sel_mat

    with col3:
        envs = ["All"] + sorted(infra_risk["corrosion_environment"].dropna().unique().tolist()) if "corrosion_environment" in infra_risk.columns else ["All"]
        default_env = params.get("env", "All")
        if default_env not in envs: default_env = "All"
        sel_env = st.selectbox("Corrosion Environment", envs, index=envs.index(default_env), key="infra_env_sel")
        st.session_state.infra_filters["env"] = sel_env

    with col4:
        risk_levels = ["All", "Critical", "High", "Medium", "Low"]
        default_risk = params.get("risk", "All")
        if default_risk not in risk_levels: default_risk = "All"
        risk_filter = st.selectbox("Risk Level", risk_levels, index=risk_levels.index(default_risk), key="infra_risk_sel")
        st.session_state.infra_filters["risk"] = risk_filter

    # Apply filters
    filtered = infra_risk.copy()
    if sel_type != "All" and "bridge_type" in filtered.columns:
        filtered = filtered[filtered["bridge_type"] == sel_type]
    if sel_mat != "All" and "material" in filtered.columns:
        filtered = filtered[filtered["material"] == sel_mat]
    if sel_env != "All" and "corrosion_environment" in filtered.columns:
        filtered = filtered[filtered["corrosion_environment"] == sel_env]
    if risk_filter != "All" and "risk_category" in filtered.columns:
        filtered = filtered[filtered["risk_category"] == risk_filter]
    filtered = filtered.reset_index(drop=True)


    # ─── KPIs ──────────────────────────────────────────────────
    section_header("Portfolio Overview", "📊")

    exposure = compute_financial_exposure(filtered)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        metric_card("Total Assets", str(len(filtered)), color="#00d9ff")
    with col2:
        metric_card("Avg Risk Score", f"{exposure['avg_risk']:.2f}", color="#f59e0b")
    with col3:
        metric_card("High Risk", str(exposure["high_risk_count"]), color="#ef4444")
    with col4:
        metric_card("Replacement Value", format_currency(exposure["total_replacement"] * 1e6), color="#3b82f6")
    with col5:
        metric_card("Outstanding Loans", format_currency(exposure["total_loans"] * 1e6), color="#7c3aed")

    st.markdown("")

    # ─── Tabs ──────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Risk Analysis", "🔧 Asset Details", "🏗️ Asset Fleet", "⚠️ Failure History", "📋 Data"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            # Risk distribution
            if "risk_category" in filtered.columns:
                risk_counts = filtered["risk_category"].value_counts().reset_index()
                risk_counts.columns = ["risk_level", "count"]
                donut_chart(risk_counts, "risk_level", "count", title="Risk Level Distribution", height=320)

        with col2:
            # Risk by material
            if "material" in filtered.columns and "risk_score" in filtered.columns:
                mat_risk = filtered.groupby("material")["risk_score"].mean().reset_index()
                mat_risk.columns = ["material", "avg_risk"]
                mat_risk = mat_risk.sort_values("avg_risk", ascending=False).head(10)
                bar_chart(mat_risk, "material", "avg_risk", title="Avg Risk by Material", height=320)

        # Risk vs Age scatter
        if "age_years" in filtered.columns and "risk_score" in filtered.columns:
            scatter_chart(
                filtered, "age_years", "risk_score",
                color="bridge_type" if "bridge_type" in filtered.columns else None,
                title="Risk Score vs Asset Age",
                height=350, x_title="Age (years)", y_title="Risk Score",
            )

    with tab2:
        st.markdown("### 🔍 Top Risk Assets")

        if "risk_score" in filtered.columns:
            top_risk = filtered.nlargest(20, "risk_score")
            display_cols = [c for c in ["bridge_id", "bridge_type", "material", "age_years",
                                         "condition_rating", "corrosion_rate_mm_yr",
                                         "risk_score", "risk_category", "replacement_cost_M"]
                           if c in top_risk.columns]
            if display_cols:
                st.dataframe(top_risk[display_cols], use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("### 🏗️ Asset Fleet Overview")
        if fleet.empty:
            st.info("No fleet data available.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                if "asset_type" in fleet.columns:
                    type_c = fleet["asset_type"].value_counts().reset_index()
                    type_c.columns = ["type", "count"]
                    bar_chart(type_c, "type", "count", title="Fleet by Asset Type")
            with col2:
                if "failure_probability" in fleet.columns:
                    histogram_chart(fleet, "failure_probability", title="Failure Probability Dist.")
            
            st.dataframe(fleet.head(200), use_container_width=True, hide_index=True)

    with tab4:
        if failures.empty:
            st.info("No historical failure data available.")
        else:
            analysis = failure_probability_analysis(failures)

            col1, col2, col3 = st.columns(3)
            with col1:
                metric_card("Total Events", str(len(failures)), color="#ef4444")
            with col2:
                metric_card("Avg Loss Ratio", f"{analysis['avg_loss_ratio']:.2f}", color="#f59e0b")
            with col3:
                metric_card("Prediction Rate", f"{analysis['prediction_rate']*100:.1f}%", color="#10b981")

            col1, col2 = st.columns(2)
            with col1:
                if not analysis["by_mode"].empty:
                    bar_chart(analysis["by_mode"], "failure_mode", "count", title="Failures by Mode", height=300)
            with col2:
                if not analysis["by_severity"].empty:
                    donut_chart(analysis["by_severity"], "severity", "count", title="Severity Distribution", height=300)

    with tab5:
        st.markdown(f"### 📋 Infrastructure Database ({len(filtered):,} records)")
        display_cols = [c for c in filtered.columns if c in [
            "bridge_id", "bridge_type", "material", "year_built", "age_years",
            "condition_rating", "corrosion_rate_mm_yr", "risk_score",
            "risk_category", "replacement_cost_M", "location",
        ]]
        st.dataframe(filtered[display_cols].head(500) if display_cols else filtered.head(500),
                     use_container_width=True, hide_index=True)

