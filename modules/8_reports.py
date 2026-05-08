"""
MatRisk AI - Reports Page
Generate and export comprehensive reports.
"""

import streamlit as st
import pandas as pd
import io
import uuid
from utils.data_loader import (
    load_materials, load_commodity_prices, load_commodities,
    load_infrastructure_assets, load_historical_failures, load_esg,
)
from utils.helpers import section_header, metric_card
from services.risk_service import compute_infrastructure_risk, compute_financial_exposure


def render():
    """Render the Reports page."""
    st.markdown("# 📋 Report Generator")
    st.markdown("Generate, preview, and export comprehensive analytics reports.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "📥 Data Export", "📄 Custom Report"])

    with tab1:
        _render_executive_summary()
    with tab2:
        _render_data_export()
    with tab3:
        _render_custom_report()


def _render_executive_summary():
    section_header("Executive Summary", "📊")
    materials = load_materials()
    infra = load_infrastructure_assets()
    failures = load_historical_failures()
    esg = load_esg()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Materials", f"{len(materials):,}", color="#00d9ff")
    with col2:
        metric_card("Assets", f"{len(infra):,}", color="#10b981")
    with col3:
        metric_card("Failures", f"{len(failures):,}", color="#ef4444")
    with col4:
        metric_card("ESG Records", str(len(esg)), color="#7c3aed")

    if not infra.empty:
        infra_risk = compute_infrastructure_risk(infra)
        exposure = compute_financial_exposure(infra_risk)
        st.markdown("### 💰 Financial Risk Summary")
        summary = pd.DataFrame({
            "Metric": ["Replacement Value", "Outstanding Loans", "Insurance/yr",
                       "Avg Risk", "High Risk Assets", "Critical Assets"],
            "Value": [f"${exposure['total_replacement']:.1f}M",
                      f"${exposure['total_loans']:.1f}M",
                      f"${exposure['total_insurance']:.1f}K",
                      f"{exposure['avg_risk']:.3f}",
                      str(exposure["high_risk_count"]),
                      str(exposure["critical_count"])],
        })
        st.dataframe(summary, use_container_width=True, hide_index=True)

    if not materials.empty:
        st.markdown("### 🧪 Material Summary")
        mat_summary = pd.DataFrame({
            "Metric": ["Total", "Categories", "Stable", "Metallic", "Avg Density"],
            "Value": [
                str(len(materials)),
                str(materials["category"].nunique()) if "category" in materials.columns else "N/A",
                str(int(materials["is_stable"].sum())) if "is_stable" in materials.columns else "N/A",
                str(int((materials["band_gap_eV"] == 0).sum())) if "band_gap_eV" in materials.columns else "N/A",
                f"{materials['density_g_cm3'].mean():.2f}" if "density_g_cm3" in materials.columns else "N/A",
            ],
        })
        st.dataframe(mat_summary, use_container_width=True, hide_index=True)


def _render_data_export():
    section_header("Data Export", "📥")
    datasets = {
        "Materials": load_materials,
        "Infrastructure": load_infrastructure_assets,
        "Failures": load_historical_failures,
        "ESG": load_esg,
        "Commodity Prices": load_commodity_prices,
        "Commodities": load_commodities,
    }
    selected = st.multiselect("Select Datasets", list(datasets.keys()),
                               default=["Materials"], key="exp_sel")
    fmt = st.radio("Format", ["CSV", "Excel"], horizontal=True, key="exp_fmt")

    if st.button("📥 Generate Export", key="gen_exp"):
        for name in selected:
            try:
                df = datasets[name]()
                if df.empty:
                    st.warning(f"{name}: empty")
                    continue
                if fmt == "CSV":
                    st.download_button(f"⬇️ {name} ({len(df):,} rows)",
                                       df.to_csv(index=False),
                                       f"matrisk_{name.lower().replace(' ','_')}.csv",
                                       "text/csv", key=f"dl_{name}")
                else:
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
                        df.to_excel(w, index=False, sheet_name=name[:31])
                    st.download_button(f"⬇️ {name} ({len(df):,} rows)",
                                       buf.getvalue(),
                                       f"matrisk_{name.lower().replace(' ','_')}.xlsx",
                                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                       key=f"dl_{name}")
                st.success(f"✅ {name} ready")
            except Exception as e:
                st.error(f"Error: {e}")


def _render_custom_report():
    section_header("Custom Report Builder", "📄")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        sections = st.multiselect(
            "Select Sections",
            ["Portfolio Overview", "Risk Summary", "Material Stats", "Failure Analysis", "ESG Impact"],
            default=st.session_state.report_builder_config["sections"] or ["Portfolio Overview", "Risk Summary"],
            key="custom_report_sections_select"
        )
        st.session_state.report_builder_config["sections"] = sections
        
        report_format = st.radio("Format", ["Markdown", "Plain Text"], index=0 if st.session_state.report_builder_config["format"] == "Markdown" else 1, key="rep_fmt")
        st.session_state.report_builder_config["format"] = report_format

        if st.button("📄 Generate Report", key="gen_custom_report_btn"):
            with st.spinner("Generating..."):
                lines = [
                    f"# MatRisk AI - Analytical Report",
                    f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    f"**Session ID:** {st.session_state.session_id}",
                    "---",
                    ""
                ]
                
                if "Portfolio Overview" in sections:
                    m, i = len(load_materials()), len(load_infrastructure_assets())
                    lines.extend(["## Portfolio Overview", f"- **Materials Tracked:** {m}", f"- **Infrastructure Assets:** {i}", ""])
                
                if "Risk Summary" in sections:
                    infra = load_infrastructure_assets()
                    if not infra.empty:
                        exp = compute_financial_exposure(compute_infrastructure_risk(infra))
                        lines.extend([
                            "## Risk Analysis", 
                            f"- **Average Risk Score:** {exp['avg_risk']:.3f}", 
                            f"- **Critical Assets Flagged:** {exp['critical_count']}",
                            f"- **Total Replacement Value:** ${exp['total_replacement']:.1f}M",
                            ""
                        ])
                
                if "Material Stats" in sections:
                    mat = load_materials()
                    if not mat.empty:
                        lines.extend([
                            "## Material Intelligence", 
                            f"- **Total Records:** {len(mat)}", 
                            f"- **Stable Candidates:** {int(mat['is_stable'].sum()) if 'is_stable' in mat.columns else 'N/A'}",
                            f"- **Categories Identified:** {mat['category'].nunique() if 'category' in mat.columns else 'N/A'}",
                            ""
                        ])

                report_content = "\n".join(lines)
                
                # Save to session history
                new_report = {
                    "id": str(uuid.uuid4())[:8],
                    "timestamp": pd.Timestamp.now().strftime('%H:%M:%S'),
                    "content": report_content,
                    "sections": sections
                }
                st.session_state.generated_reports.insert(0, new_report)
                st.success("Report generated successfully!")

    with col2:
        st.markdown("### 📜 Report History")
        if not st.session_state.generated_reports:
            st.info("No reports generated in this session yet.")
        else:
            for i, rep in enumerate(st.session_state.generated_reports):
                with st.expander(f"Report {rep['id']} - {rep['timestamp']}"):
                    st.markdown(rep["content"])
                    st.download_button(
                        f"⬇️ Download {rep['id']}", 
                        rep["content"], 
                        f"matrisk_report_{rep['id']}.md", 
                        "text/markdown",
                        key=f"dl_rep_{rep['id']}"
                    )
                    if st.button(f"🗑️ Delete", key=f"del_rep_{rep['id']}"):
                        st.session_state.generated_reports.pop(i)
                        st.rerun()


