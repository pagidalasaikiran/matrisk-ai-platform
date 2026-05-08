"""
MatRisk AI - Commodities Analytics Page
Price tracking, technical analysis, and trend predictions.
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_commodity_prices, load_commodities
from utils.helpers import metric_card, section_header, empty_state, format_currency
from components.charts import line_chart, bar_chart, scatter_chart, histogram_chart, area_chart
from services.ml_service import predict_commodity_trend
from services.risk_service import compute_var, compute_cvar


def render():
    """Render the Commodities Analytics page."""
    st.markdown("# 📈 Commodity Market Analytics")
    st.markdown("Track prices, analyze trends, and assess commodity risk exposure.")
    st.markdown("---")

    prices = load_commodity_prices()
    commodities = load_commodities()

    # Use whichever is available, prefer the larger dataset
    if not prices.empty:
        main_df = prices
        source = "Historical Prices"
    elif not commodities.empty:
        main_df = commodities
        source = "Synthetic Commodities"
    else:
        empty_state("No commodity data loaded.")
        return

    # ─── Commodity Selector ────────────────────────────────────
    section_header("Market Overview", "📊")

    available_commodities = sorted(main_df["commodity"].dropna().unique().tolist()) if "commodity" in main_df.columns else []

    if not available_commodities:
        st.warning("No commodities found in dataset.")
        return

    # Sync with session state
    default_comm = st.session_state.comm_filters.get("selected_commodity")
    if default_comm not in available_commodities: default_comm = available_commodities[0] if available_commodities else None

    col1, col2 = st.columns([1, 3])
    with col1:
        selected = st.selectbox("Select Commodity", available_commodities, 
                                 index=available_commodities.index(default_comm) if default_comm else 0,
                                 key="comm_select_box")
        st.session_state.comm_filters["selected_commodity"] = selected

    with col2:
        st.caption(f"Data source: {source} | {len(main_df):,} records")

    # Filter to selected commodity
    cdf = main_df[main_df["commodity"] == selected].sort_values("date").reset_index(drop=True)


    if cdf.empty:
        st.warning(f"No data for {selected}.")
        return

    # ─── KPIs ──────────────────────────────────────────────────
    latest = cdf.iloc[-1] if len(cdf) > 0 else pd.Series()
    prev = cdf.iloc[-2] if len(cdf) > 1 else pd.Series()

    last_close = float(latest.get("close", 0))
    prev_close = float(prev.get("close", last_close)) if not prev.empty else last_close
    change = last_close - prev_close
    change_pct = (change / prev_close * 100) if prev_close != 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        color = "#10b981" if change >= 0 else "#ef4444"
        metric_card("Last Price", f"${last_close:.2f}", delta=f"{'+'if change>=0 else ''}{change_pct:.2f}%", color=color)
    with col2:
        high = float(latest.get("high", 0))
        metric_card("Day High", f"${high:.2f}", color="#3b82f6")
    with col3:
        low = float(latest.get("low", 0))
        metric_card("Day Low", f"${low:.2f}", color="#f59e0b")
    with col4:
        vol = float(latest.get("volume", 0))
        metric_card("Volume", f"{vol:,.0f}", color="#7c3aed")
    with col5:
        rsi = float(latest.get("rsi_14", latest.get("RSI", 50)))
        rsi_color = "#ef4444" if rsi > 70 else "#10b981" if rsi < 30 else "#f59e0b"
        metric_card("RSI", f"{rsi:.1f}", color=rsi_color)

    st.markdown("")

    # ─── Tabs ──────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Price Chart", "📊 Technical", "🤖 Predictions", "📋 Data"])

    with tab1:
        # Price chart
        if "date" in cdf.columns and "close" in cdf.columns:
            line_chart(cdf, "date", "close", title=f"{selected} - Price History", height=400,
                       x_title="Date", y_title="Price ($)")

        # Volume chart
        if "date" in cdf.columns and "volume" in cdf.columns:
            area_chart(cdf, "date", "volume", title=f"{selected} - Trading Volume", height=250)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            # Returns distribution
            if "daily_return" in cdf.columns:
                returns = cdf["daily_return"].dropna()
                histogram_chart(cdf.dropna(subset=["daily_return"]), "daily_return", bins=50,
                                title="Daily Return Distribution", height=300)

                # VaR and CVaR
                var_95 = compute_var(returns, 0.95)
                cvar_95 = compute_cvar(returns, 0.95)
                col_a, col_b = st.columns(2)
                with col_a:
                    metric_card("VaR (95%)", f"{var_95*100:.2f}%", color="#ef4444")
                with col_b:
                    metric_card("CVaR (95%)", f"{cvar_95*100:.2f}%", color="#ef4444")

            elif "volatility" in cdf.columns:
                histogram_chart(cdf.dropna(subset=["volatility"]), "volatility", bins=30,
                                title="Volatility Distribution", height=300)

        with col2:
            # RSI chart
            rsi_col = "rsi_14" if "rsi_14" in cdf.columns else "RSI" if "RSI" in cdf.columns else None
            if rsi_col and "date" in cdf.columns:
                line_chart(cdf.dropna(subset=[rsi_col]), "date", rsi_col,
                          title="RSI (14-day)", height=300, y_title="RSI")

            # Volatility time series
            vol_col = "volatility_21d_ann" if "volatility_21d_ann" in cdf.columns else "volatility" if "volatility" in cdf.columns else None
            if vol_col and "date" in cdf.columns:
                line_chart(cdf.dropna(subset=[vol_col]), "date", vol_col,
                          title="Annualized Volatility", height=300, y_title="Volatility")

    with tab3:
        st.markdown("### 🤖 Commodity Trend Analysis")

        if st.button("🚀 Run Trend Analysis", key="run_trend"):
            with st.spinner("Analyzing commodity trends..."):
                result = predict_commodity_trend(main_df)
                pred_df = result.get("predictions", pd.DataFrame())

                if not pred_df.empty:
                    st.dataframe(pred_df, use_container_width=True, hide_index=True)

                    # Signal distribution
                    if "signal" in pred_df.columns:
                        sig_counts = pred_df["signal"].value_counts().reset_index()
                        sig_counts.columns = ["signal", "count"]
                        bar_chart(sig_counts, "signal", "count", title="Trading Signals", height=280)
                else:
                    st.info("Insufficient data for trend analysis.")

    with tab4:
        st.markdown(f"### 📋 {selected} Price Data ({len(cdf):,} records)")
        display_cols = [c for c in cdf.columns if c in [
            "date", "open", "high", "low", "close", "volume",
            "daily_return", "rsi_14", "RSI", "volatility",
            "trend_label", "Bollinger_bands", "moving_averages",
        ]]
        st.dataframe(cdf[display_cols].tail(200) if display_cols else cdf.tail(200),
                     use_container_width=True, hide_index=True)
