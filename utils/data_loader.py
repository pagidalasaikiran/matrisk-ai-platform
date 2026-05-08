"""
MatRisk AI - Defensive Data Loader
All CSV loading with schema validation, fallback defaults, and caching.
"""

import pandas as pd
import numpy as np
import streamlit as st
import os
from utils.constants import (
    MATERIALS_CSV, COMMODITY_PRICES_CSV, COMMODITIES_CSV,
    INFRASTRUCTURE_ASSETS_CSV, INFRASTRUCTURE_CSV,
    HISTORICAL_FAILURES_CSV, ESG_CSV,
)


from pathlib import Path

def _safe_read_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Read CSV with defensive error handling. Returns empty DataFrame on failure."""
    try:
        # Convert path to Path object if it's a string
        p = Path(path)
        if not p.exists():
            st.warning(f"Dataset not found: {p.name}")
            return pd.DataFrame()
        df = pd.read_csv(p, **kwargs)
        if df.empty:
            st.warning(f"Dataset is empty: {p.name}")
        return df
    except Exception as e:
        # Safely get the name of the file
        fname = Path(path).name if path else "unknown"
        st.error(f"Error loading {fname}: {e}")
        return pd.DataFrame()



def _coerce_numeric(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Coerce columns to numeric, ignoring errors."""
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _coerce_datetime(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Coerce columns to datetime, ignoring errors."""
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _safe_col(df: pd.DataFrame, col: str, default=None):
    """Safely get a column, returning default Series if missing."""
    if col in df.columns:
        return df[col]
    return pd.Series([default] * len(df), name=col)


# ─── Cached Loaders ───────────────────────────────────────────

@st.cache_data(ttl=600)
def load_materials() -> pd.DataFrame:
    """Load materials dataset with defensive type coercion."""
    df = _safe_read_csv(MATERIALS_CSV)
    if df.empty:
        return df
    numeric_cols = [
        "n_elements", "spacegroup_number", "formation_energy_per_atom_eV",
        "energy_above_hull_eV", "band_gap_eV", "is_metal",
        "bulk_modulus_GPa", "shear_modulus_GPa", "poisson_ratio",
        "density_g_cm3", "nsites", "volume_A3", "melting_point_K", "is_stable",
    ]
    df = _coerce_numeric(df, numeric_cols)
    df = df.dropna(subset=["material_id"]).reset_index(drop=True)
    return df


@st.cache_data(ttl=600)
def load_commodity_prices() -> pd.DataFrame:
    """Load commodity_prices dataset with date parsing."""
    df = _safe_read_csv(COMMODITY_PRICES_CSV)
    if df.empty:
        return df
    df = _coerce_datetime(df, ["date"])
    numeric_cols = [
        "open", "high", "low", "close", "volume",
        "daily_return", "return_5d", "return_21d",
        "volatility_5d_ann", "volatility_21d_ann", "volatility_63d_ann",
        "sma_21", "sma_63", "bollinger_upper", "bollinger_lower",
        "bollinger_z", "rsi_14", "macd", "macd_signal",
        "momentum_10d", "momentum_21d", "term_spread",
    ]
    df = _coerce_numeric(df, numeric_cols)
    df = df.dropna(subset=["date", "commodity"]).reset_index(drop=True)
    df = df.sort_values(["commodity", "date"]).reset_index(drop=True)
    return df


@st.cache_data(ttl=600)
def load_commodities() -> pd.DataFrame:
    """Load commodities (synthetic) dataset."""
    df = _safe_read_csv(COMMODITIES_CSV)
    if df.empty:
        return df
    df = _coerce_datetime(df, ["date"])
    numeric_cols = ["open", "high", "low", "close", "volume", "volatility", "RSI"]
    df = _coerce_numeric(df, numeric_cols)
    df = df.dropna(subset=["date", "commodity"]).reset_index(drop=True)
    df = df.sort_values(["commodity", "date"]).reset_index(drop=True)
    return df


@st.cache_data(ttl=600)
def load_infrastructure_assets() -> pd.DataFrame:
    """Load infrastructure_assets (bridge) dataset."""
    df = _safe_read_csv(INFRASTRUCTURE_ASSETS_CSV)
    if df.empty:
        return df
    numeric_cols = [
        "year_built", "age_years", "design_life_years",
        "corrosion_rate_mm_yr", "condition_rating", "structurally_deficient",
        "adt", "deck_area_sqft", "tensile_strength_MPa", "yield_strength_MPa",
        "paris_C", "paris_m", "original_thickness_mm", "remaining_thickness_mm",
        "fatigue_cycles_millions", "replacement_cost_M", "loan_outstanding_M",
        "insurance_premium_K_yr",
    ]
    df = _coerce_numeric(df, numeric_cols)
    df = _coerce_datetime(df, ["last_inspection_date"])
    df = df.dropna(subset=["bridge_id"]).reset_index(drop=True)
    return df


@st.cache_data(ttl=600)
def load_infrastructure() -> pd.DataFrame:
    """Load infrastructure (small assets) dataset."""
    df = _safe_read_csv(INFRASTRUCTURE_CSV)
    if df.empty:
        return df
    numeric_cols = [
        "age", "traffic_load", "corrosion_exposure", "condition_rating",
        "maintenance_cost", "loan_amount", "insurance_risk",
        "failure_probability", "remaining_life",
    ]
    df = _coerce_numeric(df, numeric_cols)
    return df


@st.cache_data(ttl=600)
def load_historical_failures() -> pd.DataFrame:
    """Load historical failures dataset."""
    df = _safe_read_csv(HISTORICAL_FAILURES_CSV)
    if df.empty:
        return df
    numeric_cols = [
        "event_year", "age_at_event_years", "corrosion_rate_mm_yr",
        "replacement_value_USD", "repair_cost_USD", "loss_ratio",
        "was_predicted", "warning_lead_months",
        "insurance_claim_filed", "regulatory_action",
    ]
    df = _coerce_numeric(df, numeric_cols)
    return df


@st.cache_data(ttl=600)
def load_esg() -> pd.DataFrame:
    """Load ESG dataset."""
    df = _safe_read_csv(ESG_CSV)
    if df.empty:
        return df
    numeric_cols = [
        "carbon_footprint", "recycled_percentage",
        "lifecycle_score", "sustainability_score", "emissions",
    ]
    df = _coerce_numeric(df, numeric_cols)
    return df


def init_database():
    """Initialize data in session state for cross-page access."""
    if "data_initialized" not in st.session_state:
        st.session_state["data_initialized"] = True


def get_dataset_summary() -> dict:
    """Get summary of all datasets for dashboard display."""
    summary = {}
    datasets = {
        "Materials": (load_materials, MATERIALS_CSV),
        "Commodity Prices": (load_commodity_prices, COMMODITY_PRICES_CSV),
        "Commodities": (load_commodities, COMMODITIES_CSV),
        "Infrastructure Assets": (load_infrastructure_assets, INFRASTRUCTURE_ASSETS_CSV),
        "Infrastructure": (load_infrastructure, INFRASTRUCTURE_CSV),
        "Historical Failures": (load_historical_failures, HISTORICAL_FAILURES_CSV),
        "ESG": (load_esg, ESG_CSV),
    }
    for name, (loader, path) in datasets.items():
        try:
            df = loader()
            summary[name] = {
                "rows": len(df),
                "columns": len(df.columns),
                "file_exists": Path(path).exists(),
                "status": "✅" if len(df) > 0 else "⚠️",
            }
        except Exception:
            summary[name] = {
                "rows": 0,
                "columns": 0,
                "file_exists": Path(path).exists(),
                "status": "❌",
            }

    return summary
