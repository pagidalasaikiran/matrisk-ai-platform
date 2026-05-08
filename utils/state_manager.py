"""
MatRisk AI - Session State Manager
Centralized initialization and management of platform-wide session state.
"""

import streamlit as st
import uuid

def init_session_state():
    """Initialize all session state keys if they don't exist."""
    
    # Platform Core
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
    
    # Page Persistence
    if "current_page" not in st.session_state:
        st.session_state.current_page = "🏠 Home"

    # --- Dashboard State ---
    if "dash_filters" not in st.session_state:
        st.session_state.dash_filters = {}

    # --- Materials State ---
    if "mat_filters" not in st.session_state:
        st.session_state.mat_filters = {
            "category": "All",
            "crystal": "All",
            "stability": "All"
        }
    if "mat_ml_results" not in st.session_state:
        st.session_state.mat_ml_results = {}

    # --- Commodities State ---
    if "comm_filters" not in st.session_state:
        st.session_state.comm_filters = {
            "selected_commodity": None
        }
    if "comm_ml_results" not in st.session_state:
        st.session_state.comm_ml_results = {}

    # --- Infrastructure State ---
    if "infra_filters" not in st.session_state:
        st.session_state.infra_filters = {
            "type": "All",
            "material": "All",
            "env": "All",
            "risk": "All"
        }

    # --- MatRisk Lab (Simulator) State ---
    if "sim_mc_params" not in st.session_state:
        st.session_state.sim_mc_params = {
            "commodity": None,
            "days": 252,
            "sims": 1000,
            "seed": 42
        }
    if "sim_mc_results" not in st.session_state:
        st.session_state.sim_mc_results = None
        
    if "sim_corr_params" not in st.session_state:
        st.session_state.sim_corr_params = {
            "thickness": 40.0,
            "rate": 0.05,
            "years": 50,
            "uncertainty": 0.2
        }
    if "sim_corr_results" not in st.session_state:
        st.session_state.sim_corr_results = None

    # --- AI Insights State ---
    if "ai_insights_history" not in st.session_state:
        st.session_state.ai_insights_history = []

    # --- Reports State ---
    if "generated_reports" not in st.session_state:
        st.session_state.generated_reports = []
    if "report_builder_config" not in st.session_state:
        st.session_state.report_builder_config = {
            "sections": [],
            "format": "Markdown"
        }

def get_state(key, default=None):
    """Safely get a value from session state."""
    return st.session_state.get(key, default)

def set_state(key, value):
    """Safely set a value in session state."""
    st.session_state[key] = value
