"""
MatRisk AI - Helper Functions
Utility functions for formatting, calculations, and UI components.
"""

import pandas as pd
import numpy as np
import streamlit as st
from utils.constants import COLORS, RISK_LEVELS


def safe_get(df: pd.DataFrame, col: str, default=None):
    """Safely get column from DataFrame."""
    if col in df.columns:
        return df[col]
    return pd.Series([default] * len(df), name=col)


def safe_metric(value, fmt=".2f", prefix="", suffix=""):
    """Format a metric value safely."""
    try:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return "N/A"
        return f"{prefix}{value:{fmt}}{suffix}"
    except (ValueError, TypeError):
        return str(value) if value is not None else "N/A"


def format_currency(value, decimals=2):
    """Format as currency string."""
    try:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return "$0.00"
        if abs(value) >= 1e9:
            return f"${value/1e9:.{decimals}f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.{decimals}f}M"
        elif abs(value) >= 1e3:
            return f"${value/1e3:.{decimals}f}K"
        else:
            return f"${value:.{decimals}f}"
    except (ValueError, TypeError):
        return "$0.00"


def format_number(value, decimals=1):
    """Format large numbers with suffixes."""
    try:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return "0"
        if abs(value) >= 1e9:
            return f"{value/1e9:.{decimals}f}B"
        elif abs(value) >= 1e6:
            return f"{value/1e6:.{decimals}f}M"
        elif abs(value) >= 1e3:
            return f"{value/1e3:.{decimals}f}K"
        else:
            return f"{value:.{decimals}f}"
    except (ValueError, TypeError):
        return "0"


def format_pct(value, decimals=1):
    """Format as percentage."""
    try:
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return "0.0%"
        return f"{value*100:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0.0%"


def get_risk_level(score: float) -> dict:
    """Get risk level info based on score (0-1)."""
    try:
        score = float(score)
    except (ValueError, TypeError):
        return {"level": "Unknown", "color": "#94a3b8"}
    for level, info in RISK_LEVELS.items():
        if score >= info["threshold"]:
            return {"level": level, "color": info["color"]}
    return {"level": "Low", "color": "#10b981"}


def risk_color(score: float) -> str:
    """Get color for a risk score."""
    return get_risk_level(score)["color"]


def metric_card(label: str, value: str, delta: str = None, color: str = None):
    """Render a styled metric card."""
    color = color or COLORS["primary"]
    delta_html = ""
    if delta:
        delta_color = COLORS["success"] if not delta.startswith("-") else COLORS["danger"]
        delta_html = f'<p style="color:{delta_color};font-size:0.85rem;margin:0;">{delta}</p>'

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['bg_card']} 0%, #1a2332 100%);
        border: 1px solid {color}33;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        border-left: 4px solid {color};
    ">
        <p style="color:{COLORS['text_muted']};font-size:0.85rem;margin:0 0 0.3rem 0;text-transform:uppercase;letter-spacing:0.05em;">{label}</p>
        <p style="color:{color};font-size:1.8rem;font-weight:700;margin:0;">{value}</p>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, icon: str = "", subtitle: str = ""):
    """Render a section header with gradient accent."""
    sub_html = f'<p style="color:{COLORS["text_muted"]};font-size:0.9rem;margin:0;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div style="margin: 1.5rem 0 1rem 0; border-bottom: 2px solid {COLORS['primary']}33; padding-bottom: 0.5rem;">
        <h2 style="color:{COLORS['primary']};margin:0;">{icon} {title}</h2>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def empty_state(message: str = "No data available", icon: str = "📭"):
    """Show an empty state placeholder."""
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 3rem;
        color: {COLORS['text_muted']};
        background: {COLORS['bg_card']};
        border-radius: 12px;
        border: 1px dashed {COLORS['primary']}33;
    ">
        <p style="font-size: 3rem; margin: 0;">{icon}</p>
        <p style="font-size: 1.1rem; margin: 0.5rem 0 0 0;">{message}</p>
    </div>
    """, unsafe_allow_html=True)


def compute_stats(series: pd.Series) -> dict:
    """Compute descriptive statistics for a numeric series."""
    clean = series.dropna()
    if len(clean) == 0:
        return {"mean": 0, "std": 0, "min": 0, "max": 0, "median": 0, "count": 0}
    return {
        "mean": float(clean.mean()),
        "std": float(clean.std()),
        "min": float(clean.min()),
        "max": float(clean.max()),
        "median": float(clean.median()),
        "count": int(len(clean)),
    }
