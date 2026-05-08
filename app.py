"""
MatRisk AI - Main Application Entry Point
Enterprise-grade AI platform for material intelligence & financial risk.
"""

import streamlit as st
import sys
import os

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.data_loader import init_database
from utils.state_manager import init_session_state
from utils.constants import APP_NAME, APP_VERSION, COLORS


def main():
    """Main application entry point."""

    st.set_page_config(
        page_title="MatRisk AI",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()
    init_database()


    # ─── Global CSS ────────────────────────────────────────────
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {{ font-family: 'Inter', sans-serif; }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0f172a 0%, #1a1f3a 100%);
        border-right: 1px solid {COLORS['primary']}22;
    }}

    .main {{
        background-color: #0f172a;
    }}

    h1 {{ color: {COLORS['primary']}; font-weight: 700; }}
    h2 {{ color: {COLORS['primary']}; font-weight: 600; }}
    h3 {{ color: #e2e8f0; font-weight: 600; }}

    [data-testid="stMetricValue"] {{ color: {COLORS['primary']}; }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLORS['bg_card']};
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        color: {COLORS['text_muted']};
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['primary']}22;
        color: {COLORS['primary']};
        border-bottom: 2px solid {COLORS['primary']};
    }}

    .stDataFrame {{ border-radius: 8px; overflow: hidden; }}

    /* Hide native Streamlit navigation if it appears */
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}
    
    /* Improve sidebar radio styling to look like a menu */
    [data-testid="stSidebar"] .stRadio > div {{
        background-color: transparent !important;
        padding: 0 !important;
    }}
    
    [data-testid="stSidebar"] .stRadio label {{
        padding: 10px 15px !important;
        border-radius: 8px !important;
        margin: 2px 0 !important;
        transition: all 0.2s ease !important;
        border: 1px solid transparent !important;
        color: {COLORS['text_muted']} !important;
    }}
    
    [data-testid="stSidebar"] .stRadio label:hover {{
        background-color: #ffffff0a !important;
        color: white !important;
    }}
    
    [data-testid="stSidebar"] .stRadio label[data-aria-selected="true"] {{
        background: linear-gradient(90deg, {COLORS['primary']}22 0%, transparent 100%) !important;
        color: {COLORS['primary']} !important;
        border-left: 3px solid {COLORS['primary']} !important;
        font-weight: 600 !important;
    }}

    div[data-testid="stExpander"] {{
        background-color: {COLORS['bg_card']};
        border: 1px solid #334155;
        border-radius: 8px;
    }}

    .stDownloadButton > button {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }}
    </style>
    """, unsafe_allow_html=True)

    # ─── Sidebar ───────────────────────────────────────────────
    # ─── Sidebar ───────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding: 1.5rem 0 1rem 0;">
            <div style="
                display: inline-block; 
                padding: 10px; 
                background: linear-gradient(135deg, {COLORS['primary']}22 0%, transparent 100%);
                border-radius: 20px;
                margin-bottom: 10px;
            ">
                <p style="font-size:3.5rem; margin:0; filter: drop-shadow(0 0 10px {COLORS['primary']}44);">🔬</p>
            </div>
            <h1 style="color:{COLORS['primary']}; margin:0; font-size:2rem; letter-spacing:-0.05rem; font-weight:800;">MatRisk AI</h1>
            <p style="color:{COLORS['text_muted']}; font-size:0.9rem; margin:0; font-weight:500;">Intelligence Engine</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "🏠 Home"

        nav_options = [
            "🏠 Home",
            "📊 Dashboard",
            "🧪 Materials",
            "📈 Commodities",
            "🏗️ Infrastructure",
            "🌱 ESG Analytics",
            "🎮 MatRisk Lab",
            "🤖 AI Insights",
            "📋 Reports",
            "⚙️ Settings",
        ]

        selection = st.radio(
            "Navigation",
            nav_options,
            index=nav_options.index(st.session_state.current_page),
            key="nav_radio",
            label_visibility="collapsed"
        )
        
        if selection != st.session_state.current_page:
            st.session_state.current_page = selection
            st.rerun()

        st.markdown("<div style='flex-grow: 1; min-height: 50px;'></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # System Info Box
        st.markdown(f"""
        <div style="padding: 1rem; border-radius: 12px; background: {COLORS['bg_card']}; border: 1px solid #ffffff11; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 5px #10b981;"></div>
                <p style="color:{COLORS['primary']}; font-size:0.75rem; margin:0; font-weight:700; text-transform: uppercase;">Node: Production</p>
            </div>
            <p style="color:{COLORS['text_muted']}; font-size:0.7rem; margin:0;">Uptime: 99.9% · v{APP_VERSION}</p>
            <p style="color:{COLORS['text_muted']}; font-size:0.7rem; margin:2px 0 0 0;">Session: <code>{st.session_state.get('session_id', 'Active')}</code></p>
        </div>
        """, unsafe_allow_html=True)

    # ─── Page Routing ──────────────────────────────────────────
    page = st.session_state.current_page

    
    if page == "🏠 Home":
        render_home()
    else:
        _safe_load_page(page)


def _safe_load_page(page: str):
    """Safely import and render a page from the modules directory."""
    page_map = {
        "📊 Dashboard": "modules.1_dashboard",
        "🧪 Materials": "modules.2_materials",
        "📈 Commodities": "modules.4_commodities",
        "🏗️ Infrastructure": "modules.3_infrastructure",
        "🌱 ESG Analytics": "modules.5_esg",
        "🎮 MatRisk Lab": "modules.6_simulator",
        "🤖 AI Insights": "modules.7_insights",
        "📋 Reports": "modules.8_reports",
        "⚙️ Settings": "modules.9_settings",
    }

    module_name = page_map.get(page)
    if not module_name:
        st.error(f"### ❌ Error: Unknown Page\nRoute for **{page}** not found in platform registry.")
        return

    try:
        import importlib
        # Clear module from sys.modules to ensure fresh load if needed (optional)
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        
        module = importlib.import_module(module_name)
        
        if hasattr(module, "render"):
            module.render()
        elif hasattr(module, "main"):
            module.main()
        else:
            st.warning(f"### ⚠️ Module Rendering Issue\nModule `{module_name}` loaded but no `render()` or `main()` function was found.")
            st.info("Please ensure the page implementation includes a standard `render()` entry point.")
            
    except ImportError as e:
        st.error(f"### 🛑 Component Missing\nFailed to load component: `{module_name}`")
        st.code(str(e), language="python")
    except Exception as e:
        st.error(f"### 💥 Runtime Crash\nAn unexpected error occurred while rendering **{page}**.")
        st.exception(e)
        if st.button("🔄 Reload Platform"):
            st.rerun()



def render_home():
    """Render the home page."""
    st.markdown(f"""
    <div style="text-align:center; padding: 2rem 0;">
        <p style="font-size:4rem; margin:0;">🔬</p>
        <h1 style="
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 800;
            margin: 0.5rem 0;
        ">MatRisk AI</h1>
        <p style="color:{COLORS['text_muted']}; font-size:1.2rem; max-width:600px; margin:0 auto;">
            Predictive Material Intelligence Platform for Financial Risk Modelling
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    modules = [
        ("🧪", "Material Analysis", "Property predictions, degradation forecasting, and risk scoring", "#00d9ff"),
        ("📈", "Trading Analytics", "Price tracking, trend predictions, and volatility analysis", "#7c3aed"),
        ("🏗️", "Infrastructure", "Asset monitoring, failure prediction, and maintenance planning", "#10b981"),
        ("🌱", "ESG Analytics", "Sustainability metrics, environmental impact, and ESG ratings", "#f59e0b"),
        ("🤖", "AI Engine", "ML predictions, pattern detection, and recommendations", "#3b82f6"),
        ("🎮", "Simulation Lab", "Monte Carlo, portfolio scenarios, and stress testing", "#ec4899"),
    ]

    for i, (icon, title, desc, color) in enumerate(modules):
        col = [col1, col2, col3][i % 3]
        with col:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {COLORS['bg_card']} 0%, #1a2332 100%);
                border: 1px solid {color}33;
                border-radius: 16px;
                padding: 1.5rem;
                text-align: center;
                margin-bottom: 1rem;
                border-top: 3px solid {color};
                min-height: 180px;
            ">
                <p style="font-size:2.5rem; margin:0;">{icon}</p>
                <h3 style="color:{color}; margin:0.5rem 0 0.3rem 0;">{title}</h3>
                <p style="color:{COLORS['text_muted']}; font-size:0.85rem; margin:0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(f"""
    <div style="text-align:center; padding:1rem;">
        <p style="color:{COLORS['text_muted']}; font-size:0.85rem;">
            {APP_NAME} v{APP_VERSION} · Built with Streamlit · © 2026 ZeTheta
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
