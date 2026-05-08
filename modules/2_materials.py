"""
MatRisk AI - Materials Analysis Page
Material property exploration, comparisons, and ML predictions.
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_materials
from utils.helpers import metric_card, section_header, empty_state, compute_stats
from components.charts import (
    scatter_chart, bar_chart, histogram_chart, heatmap_chart,
)
from services.ml_service import predict_material_stability, predict_material_property


def render():
    """Render the Materials Analysis page."""
    st.markdown("# 🧪 Material Intelligence")
    st.markdown("Explore material properties, predict stability, and compare candidates.")
    st.markdown("---")

    materials = load_materials()

    if materials.empty:
        empty_state("No materials data loaded. Check datasets/processed/materials.csv")
        return

    # ─── Filters ───────────────────────────────────────────────
    section_header("Filters", "🔍")

    col1, col2, col3 = st.columns(3)

    with col1:
        categories = ["All"] + sorted(materials["category"].dropna().unique().tolist()) if "category" in materials.columns else ["All"]
        # Sync with session state
        default_cat = st.session_state.mat_filters.get("category", "All")
        if default_cat not in categories: default_cat = "All"
        selected_cat = st.selectbox("Category", categories, index=categories.index(default_cat), key="mat_cat_select")
        st.session_state.mat_filters["category"] = selected_cat

    with col2:
        crystal_systems = ["All"] + sorted(materials["crystal_system"].dropna().unique().tolist()) if "crystal_system" in materials.columns else ["All"]
        default_crystal = st.session_state.mat_filters.get("crystal", "All")
        if default_crystal not in crystal_systems: default_crystal = "All"
        selected_crystal = st.selectbox("Crystal System", crystal_systems, index=crystal_systems.index(default_crystal), key="mat_crystal_select")
        st.session_state.mat_filters["crystal"] = selected_crystal

    with col3:
        default_stab = st.session_state.mat_filters.get("stability", "All")
        stab_options = ["All", "Stable", "Unstable"]
        stability = st.selectbox("Stability", stab_options, index=stab_options.index(default_stab), key="mat_stability_select")
        st.session_state.mat_filters["stability"] = stability

    # Apply filters
    filtered = materials.copy()
    if selected_cat != "All" and "category" in filtered.columns:
        filtered = filtered[filtered["category"] == selected_cat]
    if selected_crystal != "All" and "crystal_system" in filtered.columns:
        filtered = filtered[filtered["crystal_system"] == selected_crystal]
    if stability != "All" and "is_stable" in filtered.columns:
        filtered = filtered[filtered["is_stable"] == (1 if stability == "Stable" else 0)]

    filtered = filtered.reset_index(drop=True)

    # ─── KPIs ──────────────────────────────────────────────────
    section_header("Material Overview", "📊")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        metric_card("Total Materials", str(len(filtered)), color="#00d9ff")
    with col2:
        stable_pct = filtered["is_stable"].mean() * 100 if "is_stable" in filtered.columns and len(filtered) > 0 else 0
        metric_card("Stable %", f"{stable_pct:.1f}%", color="#10b981")
    with col3:
        metal_pct = (filtered["band_gap_eV"] == 0).mean() * 100 if "band_gap_eV" in filtered.columns and len(filtered) > 0 else 0
        metric_card("Metallic %", f"{metal_pct:.1f}%", color="#7c3aed")
    with col4:
        avg_density = filtered["density_g_cm3"].mean() if "density_g_cm3" in filtered.columns else 0
        metric_card("Avg Density", f"{avg_density:.2f} g/cm³", color="#f59e0b")
    with col5:
        avg_bulk = filtered["bulk_modulus_GPa"].mean() if "bulk_modulus_GPa" in filtered.columns else 0
        metric_card("Avg Bulk Mod.", f"{avg_bulk:.1f} GPa", color="#3b82f6")

    st.markdown("")

    # ─── Property Explorer ─────────────────────────────────────
    section_header("Property Explorer", "🔬")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Distributions", "🔗 Correlations", "🤖 ML Predictions", "📋 Data Table"])

    with tab1:
        col1, col2 = st.columns(2)
        numeric_cols = [c for c in filtered.select_dtypes(include=[np.number]).columns
                       if c not in ["is_metal", "is_stable", "spacegroup_number"]]

        with col1:
            prop1 = st.selectbox("Property", numeric_cols[:len(numeric_cols)//2 + 1] if numeric_cols else [], key="hist_prop1")
            if prop1:
                histogram_chart(filtered, prop1, bins=40, title=f"Distribution: {prop1}", height=300)

        with col2:
            prop2 = st.selectbox("Property", numeric_cols[len(numeric_cols)//2 + 1:] if len(numeric_cols) > 1 else numeric_cols, key="hist_prop2")
            if prop2:
                histogram_chart(filtered, prop2, bins=40, title=f"Distribution: {prop2}", height=300)

        # Category breakdown
        if "category" in filtered.columns:
            cat_counts = filtered["category"].value_counts().head(10).reset_index()
            cat_counts.columns = ["category", "count"]
            bar_chart(cat_counts, "category", "count", title="Materials by Category", height=300)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            x_prop = st.selectbox("X-axis", numeric_cols, index=0 if numeric_cols else 0, key="scatter_x")
        with col2:
            y_prop = st.selectbox("Y-axis", numeric_cols, index=min(1, len(numeric_cols)-1) if numeric_cols else 0, key="scatter_y")

        color_by = st.selectbox("Color by", ["None", "category", "crystal_system", "is_stable", "is_metal"], key="scatter_color")
        color_col = None if color_by == "None" else color_by

        if x_prop and y_prop:
            scatter_chart(
                filtered.sample(min(2000, len(filtered)), random_state=42),
                x_prop, y_prop, color=color_col,
                title=f"{y_prop} vs {x_prop}",
                height=400,
            )

    with tab3:
        st.markdown("### 🤖 ML-Powered Predictions")

        ml_tab1, ml_tab2 = st.tabs(["Stability Prediction", "Property Prediction"])

        with ml_tab1:
            if st.button("🚀 Train Stability Model", key="train_stability"):
                with st.spinner("Training gradient boosting classifier..."):
                    result = predict_material_stability(materials)
                    st.session_state.mat_ml_results["stability"] = result
            
            # Persistent results display
            if "stability" in st.session_state.mat_ml_results:
                result = st.session_state.mat_ml_results["stability"]
                if result["accuracy"] > 0:
                    col1, col2 = st.columns(2)
                    with col1:
                        metric_card("Model Accuracy", f"{result['accuracy']*100:.1f}%", color="#10b981")
                    with col2:
                        metric_card("Test Samples", str(len(result.get("y_test", []))), color="#3b82f6")

                    if result.get("feature_importances"):
                        imp_df = pd.DataFrame([
                            {"Feature": k, "Importance": v}
                            for k, v in sorted(result["feature_importances"].items(), key=lambda x: -x[1])
                        ])
                        bar_chart(imp_df, "Feature", "Importance", title="Feature Importances", height=300)
                else:
                    st.warning("Insufficient data for training. Need at least 20 complete samples.")

        with ml_tab2:
            target = st.selectbox("Target Property", [
                "bulk_modulus_GPa", "shear_modulus_GPa", "melting_point_K",
                "density_g_cm3", "band_gap_eV",
            ], key="ml_target")

            if st.button("🚀 Train Property Model", key="train_property"):
                with st.spinner(f"Training random forest for {target}..."):
                    result = predict_material_property(materials, target)
                    st.session_state.mat_ml_results[f"prop_{target}"] = result
            
            # Persistent results display
            result_key = f"prop_{target}"
            if result_key in st.session_state.mat_ml_results:
                result = st.session_state.mat_ml_results[result_key]
                if result["r2"] > 0:
                    col1, col2 = st.columns(2)
                    with col1:
                        metric_card("R² Score", f"{result['r2']:.3f}", color="#10b981")
                    with col2:
                        metric_card("MAE", f"{result['mae']:.3f}", color="#f59e0b")

                    if result.get("feature_importances"):
                        imp_df = pd.DataFrame([
                            {"Feature": k, "Importance": v}
                            for k, v in sorted(result["feature_importances"].items(), key=lambda x: -x[1])
                        ])
                        bar_chart(imp_df, "Feature", "Importance", title="Feature Importances", height=300)
                else:
                    st.warning("Insufficient data for training.")


    with tab4:
        st.markdown(f"### 📋 Materials Database ({len(filtered):,} records)")
        display_cols = [c for c in filtered.columns if c in [
            "material_id", "formula", "category", "crystal_system",
            "formation_energy_per_atom_eV", "band_gap_eV", "is_metal",
            "bulk_modulus_GPa", "density_g_cm3", "melting_point_K", "is_stable",
        ]]
        if display_cols:
            st.dataframe(filtered[display_cols].head(500), use_container_width=True, hide_index=True)
        else:
            st.dataframe(filtered.head(500), use_container_width=True, hide_index=True)
