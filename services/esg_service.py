"""
MatRisk AI - ESG Service
Environmental, Social, and Governance analytics.
"""

import pandas as pd
import numpy as np


def compute_esg_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Compute composite ESG scores from raw metrics."""
    if df.empty:
        return df

    result = df.copy()

    # Normalize carbon footprint (lower is better)
    if "carbon_footprint" in result.columns:
        cf = result["carbon_footprint"].fillna(0)
        max_cf = cf.max() if cf.max() > 0 else 1
        result["carbon_score"] = np.clip(1 - (cf / max_cf), 0, 1)
    else:
        result["carbon_score"] = 0.5

    # Recycled percentage (higher is better)
    if "recycled_percentage" in result.columns:
        rp = result["recycled_percentage"].fillna(0)
        result["recycle_score"] = np.clip(rp / 100, 0, 1)
    else:
        result["recycle_score"] = 0.5

    # Emissions score (lower is better)
    if "emissions" in result.columns:
        em = result["emissions"].fillna(0)
        max_em = em.max() if em.max() > 0 else 1
        result["emissions_score"] = np.clip(1 - (em / max_em), 0, 1)
    else:
        result["emissions_score"] = 0.5

    # Composite ESG
    result["composite_esg"] = (
        result.get("carbon_score", 0.5) * 0.30 +
        result.get("recycle_score", 0.5) * 0.20 +
        result.get("sustainability_score", pd.Series([0.5] * len(result))) * 0.25 +
        result.get("lifecycle_score", pd.Series([0.5] * len(result))) * 0.15 +
        result.get("emissions_score", 0.5) * 0.10
    )

    return result


def get_esg_summary(df: pd.DataFrame) -> dict:
    """Generate ESG summary statistics."""
    if df.empty:
        return {
            "avg_carbon": 0, "avg_sustainability": 0,
            "avg_recycled": 0, "best_material": "N/A",
            "worst_material": "N/A", "rating_distribution": {},
        }

    avg_carbon = float(df["carbon_footprint"].mean()) if "carbon_footprint" in df.columns else 0
    avg_sust = float(df["sustainability_score"].mean()) if "sustainability_score" in df.columns else 0
    avg_recycled = float(df["recycled_percentage"].mean()) if "recycled_percentage" in df.columns else 0

    best = "N/A"
    worst = "N/A"
    if "sustainability_score" in df.columns and "material" in df.columns:
        best = str(df.loc[df["sustainability_score"].idxmax(), "material"])
        worst = str(df.loc[df["sustainability_score"].idxmin(), "material"])

    rating_dist = {}
    if "ESG_rating" in df.columns:
        rating_dist = df["ESG_rating"].value_counts().to_dict()

    return {
        "avg_carbon": avg_carbon,
        "avg_sustainability": avg_sust,
        "avg_recycled": avg_recycled,
        "best_material": best,
        "worst_material": worst,
        "rating_distribution": rating_dist,
    }


def esg_comparison(df: pd.DataFrame, materials: list) -> pd.DataFrame:
    """Compare ESG metrics for selected materials."""
    if df.empty or not materials:
        return pd.DataFrame()
    if "material" not in df.columns:
        return pd.DataFrame()
    return df[df["material"].isin(materials)].reset_index(drop=True)
