"""
MatRisk AI - AI Insights Page
Cross-domain AI-powered insights and recommendations.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_materials, load_infrastructure_assets,
    load_historical_failures, load_esg,
)
from utils.helpers import section_header, metric_card, empty_state
from utils.constants import COLORS
from services.ml_service import generate_ai_insights


def render():
    """Render the AI Insights page."""
    st.markdown("# 🤖 AI-Powered Insights")
    st.markdown("Cross-domain intelligence combining materials, infrastructure, risk, and ESG data.")
    st.markdown("---")

    # Load all datasets
    materials = load_materials()
    infra = load_infrastructure_assets()
    failures = load_historical_failures()
    esg = load_esg()

    # ─── Data Coverage ─────────────────────────────────────────
    section_header("Data Coverage", "📦")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Materials", f"{len(materials):,}", color="#00d9ff")
    with col2:
        metric_card("Infrastructure", f"{len(infra):,}", color="#10b981")
    with col3:
        metric_card("Failure Events", f"{len(failures):,}", color="#ef4444")
    with col4:
        metric_card("ESG Records", str(len(esg)), color="#7c3aed")

    st.markdown("")

    # ─── Generate Insights ─────────────────────────────────────
    section_header("AI-Generated Insights", "💡")

    insights = generate_ai_insights(materials, infra, failures, esg)

    for insight in insights:
        severity = insight.get("severity", "info")
        border_color = {
            "info": COLORS["info"],
            "warning": COLORS["warning"],
            "danger": COLORS["danger"],
            "success": COLORS["success"],
        }.get(severity, COLORS["info"])

        st.markdown(f"""
        <div style="
            background: {COLORS['bg_card']};
            border-left: 4px solid {border_color};
            border-radius: 8px;
            padding: 1rem 1.5rem;
            margin-bottom: 1rem;
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.3rem;">{insight.get('icon', 'ℹ️')}</span>
                <span style="color: {COLORS['text']}; font-weight: 600; font-size: 1.05rem;">{insight.get('title', '')}</span>
                <span style="
                    background: {border_color}22;
                    color: {border_color};
                    font-size: 0.7rem;
                    padding: 0.15rem 0.5rem;
                    border-radius: 4px;
                    text-transform: uppercase;
                    margin-left: auto;
                ">{insight.get('category', '')}</span>
            </div>
            <p style="color: {COLORS['text_muted']}; margin: 0; font-size: 0.95rem; line-height: 1.5;">
                {insight.get('detail', '')}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # ─── Cross-Domain Analysis ─────────────────────────────────
    section_header("Cross-Domain Analysis", "🔗")

    tab1, tab2, tab3 = st.tabs(["🧪 Material-Infrastructure", "📊 Failure Patterns", "🌱 ESG Impact"])

    with tab1:
        st.markdown("### Material Usage in Infrastructure")
        if not infra.empty and "material" in infra.columns:
            mat_infra = infra["material"].value_counts().head(10).reset_index()
            mat_infra.columns = ["material", "asset_count"]
            st.dataframe(mat_infra, use_container_width=True, hide_index=True)

            if "condition_rating" in infra.columns:
                avg_cond = infra.groupby("material")["condition_rating"].mean().reset_index()
                avg_cond.columns = ["material", "avg_condition"]
                avg_cond = avg_cond.sort_values("avg_condition").head(10).reset_index(drop=True)
                st.markdown("**Materials with Lowest Average Condition:**")
                st.dataframe(avg_cond, use_container_width=True, hide_index=True)
        else:
            st.info("No infrastructure material data available.")

    with tab2:
        st.markdown("### Historical Failure Patterns")
        if not failures.empty:
            col1, col2 = st.columns(2)
            with col1:
                if "failure_mode" in failures.columns and "severity" in failures.columns:
                    cross = pd.crosstab(failures["failure_mode"], failures["severity"])
                    st.markdown("**Failure Mode × Severity Matrix:**")
                    st.dataframe(cross, use_container_width=True)

            with col2:
                if "detected_by" in failures.columns:
                    det_counts = failures["detected_by"].value_counts().reset_index()
                    det_counts.columns = ["method", "count"]
                    st.markdown("**Detection Methods:**")
                    st.dataframe(det_counts, use_container_width=True, hide_index=True)

            if "event_year" in failures.columns:
                yearly = failures["event_year"].value_counts().sort_index().reset_index()
                yearly.columns = ["year", "events"]
                st.markdown("**Failures by Year:**")
                st.dataframe(yearly, use_container_width=True, hide_index=True)
        else:
            st.info("No failure data available.")

    with tab3:
        st.markdown("### ESG Material Impact Assessment")
        if not esg.empty:
            # Material risk + ESG mapping
            if "material" in esg.columns:
                st.dataframe(esg, use_container_width=True, hide_index=True)

                # Identify high-risk ESG materials
                if "carbon_footprint" in esg.columns and "sustainability_score" in esg.columns:
                    high_carbon = esg[esg["carbon_footprint"] > esg["carbon_footprint"].median()]
                    low_sust = esg[esg["sustainability_score"] < esg["sustainability_score"].median()]

                    concern = pd.merge(high_carbon, low_sust, how="inner")
                    if not concern.empty:
                        st.markdown("**⚠️ Materials of Concern** (high carbon + low sustainability):")
                        st.dataframe(concern[["material", "carbon_footprint", "sustainability_score", "ESG_rating"]],
                                    use_container_width=True, hide_index=True)
                    else:
                        st.success("No materials flagged as high concern.")
        else:
            st.info("No ESG data available.")
