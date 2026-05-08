"""
MatRisk AI - MatRisk Lab (Simulator) Page
Monte Carlo simulation, corrosion modeling, and stress testing.
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_commodity_prices, load_commodities, load_infrastructure_assets
from utils.helpers import metric_card, section_header, empty_state, format_currency
from components.charts import line_chart, histogram_chart, bar_chart
from services.simulation_service import (
    monte_carlo_price, stress_test_scenario, corrosion_simulation,
)


def render():
    """Render the MatRisk Lab page."""
    st.markdown("# 🎮 MatRisk Lab")
    st.markdown("Run simulations, stress tests, and scenario analyses.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📈 Monte Carlo", "🔧 Corrosion Sim", "💥 Stress Test"])

    with tab1:
        _render_monte_carlo()

    with tab2:
        _render_corrosion()

    with tab3:
        _render_stress_test()


def _render_monte_carlo():
    """Monte Carlo price simulation."""
    section_header("Monte Carlo Price Simulation", "📈")

    prices = load_commodity_prices()
    commodities_df = load_commodities()
    source_df = prices if not prices.empty else commodities_df

    if source_df.empty:
        empty_state("No commodity data available for simulation.")
        return

    available = sorted(source_df["commodity"].dropna().unique().tolist())

    col1, col2, col3, col4 = st.columns(4)

    # Load defaults from session state
    params = st.session_state.sim_mc_params

    with col1:
        default_comm = params.get("commodity")
        if default_comm not in available: default_comm = available[0] if available else None
        commodity = st.selectbox("Commodity", available, index=available.index(default_comm) if default_comm else 0, key="mc_commodity_select")
        st.session_state.sim_mc_params["commodity"] = commodity
    with col2:
        days = st.slider("Forecast Days", 30, 504, params.get("days", 252), key="mc_days_select")
        st.session_state.sim_mc_params["days"] = days
    with col3:
        simulations = st.slider("Simulations", 100, 5000, params.get("sims", 1000), step=100, key="mc_sims_select")
        st.session_state.sim_mc_params["sims"] = simulations
    with col4:
        seed = st.number_input("Random Seed", value=params.get("seed", 42), key="mc_seed_select")
        st.session_state.sim_mc_params["seed"] = seed

    cdf = source_df[source_df["commodity"] == commodity].sort_values("date")

    if len(cdf) < 10:
        st.warning(f"Insufficient data for {commodity}.")
        return

    last_price = float(cdf["close"].iloc[-1])

    # Calculate mu and sigma from historical data
    if "daily_return" in cdf.columns:
        returns = cdf["daily_return"].dropna()
    else:
        returns = cdf["close"].pct_change().dropna()

    mu = float(returns.mean()) * 252
    sigma = float(returns.std()) * np.sqrt(252)

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Last Price", f"${last_price:.2f}", color="#00d9ff")
    with col2:
        metric_card("Ann. Return (μ)", f"{mu*100:.1f}%", color="#10b981" if mu > 0 else "#ef4444")
    with col3:
        metric_card("Ann. Volatility (σ)", f"{sigma*100:.1f}%", color="#f59e0b")

    if st.button("🚀 Run Simulation", key="run_mc"):
        with st.spinner("Running Monte Carlo simulation..."):
            result = monte_carlo_price(last_price, mu, sigma, days, simulations, int(seed))
            st.session_state.sim_mc_results = result

    # Persistent results display
    if st.session_state.sim_mc_results:
        result = st.session_state.sim_mc_results
        
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("Mean Final", f"${result['mean_final']:.2f}", color="#00d9ff")
        with col2:
            metric_card("5th Percentile", f"${result['p5']:.2f}", color="#ef4444")
        with col3:
            metric_card("95th Percentile", f"${result['p95']:.2f}", color="#10b981")
        with col4:
            metric_card("P(Price Up)", f"{result['prob_up']*100:.1f}%", color="#7c3aed")

        # Plot sample paths
        n_show = min(50, len(result["paths"][0]))
        paths = result["paths"]
        path_df_rows = []
        for i in range(n_show):
            for t in range(0, len(paths), max(1, len(paths)//100)):
                path_df_rows.append({"day": t, "price": float(paths[t, i]), "simulation": f"Sim {i+1}"})
        path_df = pd.DataFrame(path_df_rows)

        if not path_df.empty:
            line_chart(path_df, "day", "price", color="simulation",
                      title=f"Monte Carlo Paths ({n_show} shown)", height=400)

        # Final price distribution
        final_df = pd.DataFrame({"final_price": result["final_prices"]})
        histogram_chart(final_df, "final_price", bins=50,
                       title="Final Price Distribution", height=300)



def _render_corrosion():
    """Corrosion degradation simulation."""
    section_header("Corrosion Degradation Simulation", "🔧")

    col1, col2, col3, col4 = st.columns(4)

    params = st.session_state.sim_corr_params

    with col1:
        thickness = st.number_input("Initial Thickness (mm)", 10.0, 100.0, params.get("thickness", 40.0), key="corr_thick_select")
        st.session_state.sim_corr_params["thickness"] = thickness
    with col2:
        rate = st.number_input("Corrosion Rate (mm/yr)", 0.001, 1.0, params.get("rate", 0.05), format="%.3f", key="corr_rate_select")
        st.session_state.sim_corr_params["rate"] = rate
    with col3:
        years = st.slider("Simulation Years", 10, 100, params.get("years", 50), key="corr_years_select")
        st.session_state.sim_corr_params["years"] = years
    with col4:
        uncertainty = st.slider("Uncertainty", 0.05, 0.5, params.get("uncertainty", 0.2), key="corr_unc_select")
        st.session_state.sim_corr_params["uncertainty"] = uncertainty

    if st.button("🚀 Run Corrosion Simulation", key="run_corr"):
        with st.spinner("Simulating corrosion degradation..."):
            result = corrosion_simulation(thickness, rate, years, uncertainty)
            st.session_state.sim_corr_results = result

    # Persistent results display
    if st.session_state.sim_corr_results:
        result = st.session_state.sim_corr_results
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("Avg Time to Failure", f"{result['avg_ttf']:.1f} yrs", color="#ef4444")
        with col2:
            metric_card("Median TTF", f"{result['median_ttf']:.1f} yrs", color="#f59e0b")
        with col3:
            metric_card("P(Fail in 10yr)", f"{result['prob_failure_10yr']*100:.1f}%", color="#ef4444")
        with col4:
            metric_card("P(Fail in 25yr)", f"{result['prob_failure_25yr']*100:.1f}%", color="#f59e0b")

        # Plot degradation paths
        deg_df = pd.DataFrame({
            "year": result["time"],
            "mean_thickness": result["mean_path"],
            "p5": result["p5"],
            "p95": result["p95"],
        })

        line_chart(deg_df, "year", "mean_thickness",
                  title="Mean Thickness Degradation", height=350,
                  x_title="Years", y_title="Thickness (mm)")



def _render_stress_test():
    """Stress testing scenarios."""
    section_header("Stress Test Scenarios", "💥")

    col1, col2 = st.columns(2)

    with col1:
        base_value = st.number_input("Base Portfolio Value ($M)", 1.0, 10000.0, 100.0, key="st_base")

    with col2:
        st.markdown("**Predefined Scenarios**")

    scenarios = {
        "Mild Recession": -0.10,
        "Moderate Downturn": -0.20,
        "Severe Crisis": -0.35,
        "COVID-like Shock": -0.30,
        "Rate Hike +200bp": -0.15,
        "Commodity Boom": 0.25,
        "Green Transition": 0.15,
        "Supply Chain Break": -0.25,
    }

    if st.button("🚀 Run Stress Test", key="run_stress"):
        with st.spinner("Running stress scenarios..."):
            result = stress_test_scenario(base_value, scenarios)

            st.dataframe(result, use_container_width=True, hide_index=True)

            bar_chart(result, "scenario", "change",
                     title="Portfolio Impact by Scenario ($M)", height=350)
