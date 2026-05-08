"""
MatRisk AI - ESG Analytics Page
Environmental, Social, and Governance sustainability analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_esg
from utils.helpers import metric_card, section_header, empty_state
from components.charts import bar_chart, scatter_chart, donut_chart
from services.esg_service import compute_esg_scores, get_esg_summary


def render():
    """Render the ESG Analytics page."""
    st.markdown("# 🌱 ESG Sustainability Analytics")
    st.markdown("Evaluate material sustainability, carbon impact, and ESG compliance.")
    st.markdown("---")

    esg = load_esg()

    if esg.empty:
        empty_state("No ESG data loaded.")
        return

    # Compute ESG scores
    esg_scored = compute_esg_scores(esg)
    summary = get_esg_summary(esg)

    # ─── KPIs ──────────────────────────────────────────────────
    section_header("ESG Overview", "📊")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        metric_card("Materials Tracked", str(len(esg)), color="#10b981")
    with col2:
        metric_card("Avg Carbon Footprint", f"{summary['avg_carbon']:.1f}", color="#ef4444")
    with col3:
        metric_card("Avg Recycled %", f"{summary['avg_recycled']:.1f}%", color="#3b82f6")
    with col4:
        metric_card("Avg Sustainability", f"{summary['avg_sustainability']:.2f}", color="#7c3aed")
    with col5:
        metric_card("Best Material", summary["best_material"], color="#10b981")

    st.markdown("")

    # ─── Tabs ──────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Ratings", "🔬 Analysis", "🔗 Comparison", "📋 Data"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            # ESG rating distribution
            if "ESG_rating" in esg.columns:
                rating_counts = esg["ESG_rating"].value_counts().reset_index()
                rating_counts.columns = ["rating", "count"]
                donut_chart(rating_counts, "rating", "count", title="ESG Rating Distribution", height=320)

        with col2:
            # Sustainability score by material
            if "material" in esg.columns and "sustainability_score" in esg.columns:
                sorted_esg = esg.sort_values("sustainability_score", ascending=False).reset_index(drop=True)
                bar_chart(sorted_esg, "material", "sustainability_score",
                         title="Sustainability Score by Material", height=320)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            # Carbon footprint
            if "material" in esg.columns and "carbon_footprint" in esg.columns:
                sorted_cf = esg.sort_values("carbon_footprint", ascending=False).reset_index(drop=True)
                bar_chart(sorted_cf, "material", "carbon_footprint",
                         title="Carbon Footprint by Material", height=320)

        with col2:
            # Emissions
            if "material" in esg.columns and "emissions" in esg.columns:
                sorted_em = esg.sort_values("emissions", ascending=False).reset_index(drop=True)
                bar_chart(sorted_em, "material", "emissions",
                         title="Emissions by Material", height=320)

        # Scatter: sustainability vs carbon
        if "carbon_footprint" in esg_scored.columns and "sustainability_score" in esg_scored.columns:
            scatter_chart(
                esg_scored, "carbon_footprint", "sustainability_score",
                color="ESG_rating" if "ESG_rating" in esg_scored.columns else None,
                title="Sustainability vs Carbon Footprint",
                height=350,
                x_title="Carbon Footprint",
                y_title="Sustainability Score",
            )

        # Recycled percentage
        if "material" in esg.columns and "recycled_percentage" in esg.columns:
            sorted_rp = esg.sort_values("recycled_percentage", ascending=False).reset_index(drop=True)
            bar_chart(sorted_rp, "material", "recycled_percentage",
                     title="Recycled Content (%)", height=300)

    with tab3:
        st.markdown("### 🔗 Material Comparison")

        if "material" in esg.columns:
            all_materials = esg["material"].tolist()
            
            # Sync with session state
            if "esg_comparison_selection" not in st.session_state:
                st.session_state.esg_comparison_selection = all_materials[:3] if len(all_materials) >= 3 else all_materials
            
            selected = st.multiselect("Select Materials to Compare", all_materials,
                                       default=st.session_state.esg_comparison_selection,
                                       key="esg_compare_multi")
            st.session_state.esg_comparison_selection = selected


            if selected:
                comparison = esg_scored[esg_scored["material"].isin(selected)].reset_index(drop=True)

                # Show comparison table
                display_cols = [c for c in comparison.columns if c in [
                    "material", "carbon_footprint", "recycled_percentage",
                    "lifecycle_score", "sustainability_score", "emissions",
                    "ESG_rating", "composite_esg",
                ]]
                st.dataframe(comparison[display_cols] if display_cols else comparison,
                            use_container_width=True, hide_index=True)

                # Comparison charts
                if "sustainability_score" in comparison.columns:
                    bar_chart(comparison, "material", "sustainability_score",
                             title="Sustainability Comparison", height=280)

                if "composite_esg" in comparison.columns:
                    bar_chart(comparison, "material", "composite_esg",
                             title="Composite ESG Score", height=280)

    with tab4:
        st.markdown(f"### 📋 ESG Database ({len(esg_scored)} materials)")
        st.dataframe(esg_scored, use_container_width=True, hide_index=True)
