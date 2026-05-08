"""
MatRisk AI - Dashboard Page
System overview with KPIs, dataset status, and quick charts.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_materials, load_commodity_prices, load_commodities,
    load_infrastructure_assets, load_historical_failures,
    load_esg, get_dataset_summary,
)
from utils.helpers import metric_card, section_header, format_number, format_currency
from components.charts import bar_chart, donut_chart, line_chart
from services.risk_service import compute_infrastructure_risk, compute_financial_exposure


def render():
    """Render the Dashboard page."""
    st.markdown("# 📊 Executive Dashboard")
    st.markdown("Real-time overview of material intelligence, risk analytics, and market signals.")
    st.markdown("---")

    # ─── Load Data ─────────────────────────────────────────────
    materials = load_materials()
    commodities = load_commodities()
    infra = load_infrastructure_assets()
    failures = load_historical_failures()
    esg = load_esg()

    # ─── KPI Row ───────────────────────────────────────────────
    section_header("Key Performance Indicators", "📈")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        metric_card("Materials", format_number(len(materials), 0), color="#00d9ff")
    with col2:
        metric_card("Commodities", str(commodities["commodity"].nunique()) if not commodities.empty and "commodity" in commodities.columns else "0", color="#7c3aed")
    with col3:
        metric_card("Infrastructure Assets", format_number(len(infra), 0), color="#10b981")
    with col4:
        metric_card("Failure Events", format_number(len(failures), 0), color="#ef4444")
    with col5:
        metric_card("ESG Materials", str(len(esg)), color="#f59e0b")

    st.markdown("")

    # ─── Financial Exposure ────────────────────────────────────
    if not infra.empty:
        infra_risk = compute_infrastructure_risk(infra)
        exposure = compute_financial_exposure(infra_risk)

        section_header("Financial Exposure Summary", "💰")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("Total Replacement Value", format_currency(exposure["total_replacement"] * 1e6), color="#3b82f6")
        with col2:
            metric_card("Outstanding Loans", format_currency(exposure["total_loans"] * 1e6), color="#f59e0b")
        with col3:
            metric_card("Annual Insurance", format_currency(exposure["total_insurance"] * 1e3), color="#10b981")
        with col4:
            metric_card("High Risk Assets", str(exposure["high_risk_count"]), color="#ef4444")

    st.markdown("")

    # ─── Charts Row ────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        section_header("Material Categories", "🧪")
        if not materials.empty and "category" in materials.columns:
            cat_counts = materials["category"].value_counts().head(8).reset_index()
            cat_counts.columns = ["category", "count"]
            bar_chart(cat_counts, "category", "count", title="Top Material Categories", height=320)
        else:
            st.info("No material data available.")

    with col2:
        section_header("Infrastructure by Type", "🏗️")
        if not infra.empty and "bridge_type" in infra.columns:
            type_counts = infra["bridge_type"].value_counts().reset_index()
            type_counts.columns = ["type", "count"]
            donut_chart(type_counts, "type", "count", title="Asset Type Distribution", height=320)
        else:
            st.info("No infrastructure data available.")

    st.markdown("")

    # ─── Commodity Trends ──────────────────────────────────────
    section_header("Latest Commodity Prices", "📈")

    if not commodities.empty and "commodity" in commodities.columns and "date" in commodities.columns:
        latest = commodities.sort_values("date").groupby("commodity").tail(1)
        if "close" in latest.columns:
            cols = st.columns(min(len(latest), 6))
            for i, (_, row) in enumerate(latest.iterrows()):
                if i < len(cols):
                    with cols[i]:
                        price = row.get("close", 0)
                        trend = row.get("trend_label", "N/A")
                        color = "#10b981" if trend == "Bullish" else "#ef4444" if trend == "Bearish" else "#f59e0b"
                        metric_card(str(row.get("commodity", "N/A")), f"${price:.2f}", delta=trend, color=color)
    else:
        st.info("No commodity data available.")

    st.markdown("")

    # ─── Failure Analysis ──────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        section_header("Failure Modes", "⚠️")
        if not failures.empty and "failure_mode" in failures.columns:
            mode_counts = failures["failure_mode"].value_counts().reset_index()
            mode_counts.columns = ["mode", "count"]
            bar_chart(mode_counts, "mode", "count", title="Failure Mode Distribution", height=300)
        else:
            st.info("No failure data available.")

    with col2:
        section_header("ESG Ratings", "🌱")
        if not esg.empty and "ESG_rating" in esg.columns:
            rating_counts = esg["ESG_rating"].value_counts().reset_index()
            rating_counts.columns = ["rating", "count"]
            bar_chart(rating_counts, "rating", "count", title="ESG Rating Distribution", height=300)
        else:
            st.info("No ESG data available.")

    st.markdown("")

    # ─── Dataset Status ────────────────────────────────────────
    section_header("Dataset Status & Quick Export", "📦")
    summary = get_dataset_summary()
    status_df = pd.DataFrame([
        {"Dataset": name, "Rows": info["rows"], "Columns": info["columns"], "Status": info["status"]}
        for name, info in summary.items()
    ])
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.dataframe(status_df, use_container_width=True, hide_index=True)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            "⬇️ Export Summary",
            status_df.to_csv(index=False),
            "matrisk_system_summary.csv",
            "text/csv",
            use_container_width=True
        )

