"""
MatRisk AI - Application Constants
All column names, dataset paths, and configuration constants.
"""
from pathlib import Path

# ─── Application ───────────────────────────────────────────────
APP_NAME = "MatRisk AI"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Predictive Material Intelligence for Financial Risk Modelling"

# ─── Paths ─────────────────────────────────────────────────────
# Resolve the project root relative to this file (utils/constants.py)
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "datasets" / "processed"


# ─── Dataset File Paths ───────────────────────────────────────
MATERIALS_CSV = DATASET_DIR / "materials.csv"
COMMODITY_PRICES_CSV = DATASET_DIR / "commodity_prices.csv"
COMMODITIES_CSV = DATASET_DIR / "commodities.csv"
INFRASTRUCTURE_ASSETS_CSV = DATASET_DIR / "infrastructure_assets.csv"
INFRASTRUCTURE_CSV = DATASET_DIR / "infrastructure.csv"
HISTORICAL_FAILURES_CSV = DATASET_DIR / "historical_failures.csv"
ESG_CSV = DATASET_DIR / "esg.csv"


# ─── Materials Columns ────────────────────────────────────────
MAT_COLS = {
    "ID": "material_id",
    "FORMULA": "formula",
    "N_ELEMENTS": "n_elements",
    "CRYSTAL_SYSTEM": "crystal_system",
    "SPACEGROUP": "spacegroup_number",
    "CATEGORY": "category",
    "FORMATION_ENERGY": "formation_energy_per_atom_eV",
    "ENERGY_ABOVE_HULL": "energy_above_hull_eV",
    "BAND_GAP": "band_gap_eV",
    "IS_METAL": "is_metal",
    "BULK_MODULUS": "bulk_modulus_GPa",
    "SHEAR_MODULUS": "shear_modulus_GPa",
    "POISSON_RATIO": "poisson_ratio",
    "DENSITY": "density_g_cm3",
    "NSITES": "nsites",
    "VOLUME": "volume_A3",
    "MELTING_POINT": "melting_point_K",
    "IS_STABLE": "is_stable",
}

# ─── Commodity Prices Columns ─────────────────────────────────
CPRICE_COLS = {
    "DATE": "date",
    "COMMODITY": "commodity",
    "OPEN": "open",
    "HIGH": "high",
    "LOW": "low",
    "CLOSE": "close",
    "VOLUME": "volume",
    "DAILY_RETURN": "daily_return",
    "RETURN_5D": "return_5d",
    "RETURN_21D": "return_21d",
    "VOL_5D": "volatility_5d_ann",
    "VOL_21D": "volatility_21d_ann",
    "VOL_63D": "volatility_63d_ann",
    "SMA_21": "sma_21",
    "SMA_63": "sma_63",
    "BB_UPPER": "bollinger_upper",
    "BB_LOWER": "bollinger_lower",
    "BB_Z": "bollinger_z",
    "RSI": "rsi_14",
    "MACD": "macd",
    "MACD_SIGNAL": "macd_signal",
    "MOM_10D": "momentum_10d",
    "MOM_21D": "momentum_21d",
    "TERM_SPREAD": "term_spread",
}

# ─── Commodities (Synthetic) Columns ──────────────────────────
COMM_COLS = {
    "DATE": "date",
    "COMMODITY": "commodity",
    "OPEN": "open",
    "HIGH": "high",
    "LOW": "low",
    "CLOSE": "close",
    "VOLUME": "volume",
    "VOLATILITY": "volatility",
    "RSI": "RSI",
    "BOLLINGER": "Bollinger_bands",
    "MA": "moving_averages",
    "TREND": "trend_label",
}

# ─── Infrastructure Assets Columns ────────────────────────────
INFRA_COLS = {
    "ID": "bridge_id",
    "TYPE": "bridge_type",
    "MATERIAL": "material",
    "YEAR_BUILT": "year_built",
    "AGE": "age_years",
    "DESIGN_LIFE": "design_life_years",
    "LOCATION": "location",
    "CORROSION_ENV": "corrosion_environment",
    "CORROSION_RATE": "corrosion_rate_mm_yr",
    "CONDITION": "condition_rating",
    "DEFICIENT": "structurally_deficient",
    "ADT": "adt",
    "DECK_AREA": "deck_area_sqft",
    "TENSILE": "tensile_strength_MPa",
    "YIELD": "yield_strength_MPa",
    "PARIS_C": "paris_C",
    "PARIS_M": "paris_m",
    "ORIG_THICKNESS": "original_thickness_mm",
    "REMAIN_THICKNESS": "remaining_thickness_mm",
    "FATIGUE_CYCLES": "fatigue_cycles_millions",
    "REPLACEMENT_COST": "replacement_cost_M",
    "LOAN": "loan_outstanding_M",
    "LAST_INSPECTION": "last_inspection_date",
    "INSURANCE_PREMIUM": "insurance_premium_K_yr",
}

# ─── Infrastructure (Small) Columns ──────────────────────────
INFRA_SMALL_COLS = {
    "ID": "asset_id",
    "TYPE": "asset_type",
    "MATERIAL": "material",
    "AGE": "age",
    "CLIMATE": "climate",
    "TRAFFIC": "traffic_load",
    "CORROSION": "corrosion_exposure",
    "CONDITION": "condition_rating",
    "MAINT_COST": "maintenance_cost",
    "LOAN": "loan_amount",
    "INS_RISK": "insurance_risk",
    "FAIL_PROB": "failure_probability",
    "REMAIN_LIFE": "remaining_life",
}

# ─── Historical Failures Columns ──────────────────────────────
FAIL_COLS = {
    "ID": "event_id",
    "YEAR": "event_year",
    "STRUCT_TYPE": "structure_type",
    "MATERIAL": "material",
    "LOCATION": "location",
    "CORROSION_ENV": "corrosion_environment",
    "AGE": "age_at_event_years",
    "CORROSION_RATE": "corrosion_rate_mm_yr",
    "FAIL_MODE": "failure_mode",
    "SEVERITY": "severity",
    "REPLACEMENT_VAL": "replacement_value_USD",
    "REPAIR_COST": "repair_cost_USD",
    "LOSS_RATIO": "loss_ratio",
    "DETECTED_BY": "detected_by",
    "WAS_PREDICTED": "was_predicted",
    "WARNING_LEAD": "warning_lead_months",
    "INS_CLAIM": "insurance_claim_filed",
    "REG_ACTION": "regulatory_action",
}

# ─── ESG Columns ──────────────────────────────────────────────
ESG_COLS = {
    "MATERIAL": "material",
    "CARBON": "carbon_footprint",
    "RECYCLED": "recycled_percentage",
    "LIFECYCLE": "lifecycle_score",
    "SUSTAINABILITY": "sustainability_score",
    "EMISSIONS": "emissions",
    "RATING": "ESG_rating",
}

# ─── Theme Colors ─────────────────────────────────────────────
COLORS = {
    "primary": "#00d9ff",
    "secondary": "#7c3aed",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
    "bg_dark": "#0f172a",
    "bg_card": "#1e293b",
    "text": "#e2e8f0",
    "text_muted": "#94a3b8",
    "gradient_start": "#00d9ff",
    "gradient_end": "#7c3aed",
}

# ─── Chart Color Scale ────────────────────────────────────────
CHART_COLORS = [
    "#00d9ff", "#7c3aed", "#10b981", "#f59e0b",
    "#ef4444", "#3b82f6", "#ec4899", "#06b6d4",
    "#8b5cf6", "#14b8a6", "#f97316", "#6366f1",
]

# ─── Risk Levels ──────────────────────────────────────────────
RISK_LEVELS = {
    "Critical": {"color": "#ef4444", "threshold": 0.8},
    "High": {"color": "#f59e0b", "threshold": 0.6},
    "Medium": {"color": "#3b82f6", "threshold": 0.4},
    "Low": {"color": "#10b981", "threshold": 0.0},
}

# ─── ESG Rating Order ─────────────────────────────────────────
ESG_RATING_ORDER = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]
