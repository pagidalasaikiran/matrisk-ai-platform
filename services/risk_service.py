"""
MatRisk AI - Risk Service
Financial risk modeling for infrastructure and materials.
"""

import pandas as pd
import numpy as np


def compute_infrastructure_risk(df: pd.DataFrame) -> pd.DataFrame:
    """Compute composite risk score for infrastructure assets."""
    if df.empty:
        return df

    result = df.copy()

    # Age risk: older = higher risk
    if "age_years" in result.columns and "design_life_years" in result.columns:
        age = result["age_years"].fillna(0)
        design = result["design_life_years"].fillna(100).replace(0, 100)
        result["age_risk"] = np.clip(age / design, 0, 1)
    else:
        result["age_risk"] = 0.5

    # Corrosion risk
    if "corrosion_rate_mm_yr" in result.columns:
        corr = result["corrosion_rate_mm_yr"].fillna(0)
        result["corrosion_risk"] = np.clip(corr / corr.quantile(0.95) if corr.quantile(0.95) > 0 else 0, 0, 1)
    else:
        result["corrosion_risk"] = 0.5

    # Condition risk (inverted — lower condition = higher risk)
    if "condition_rating" in result.columns:
        cond = result["condition_rating"].fillna(5)
        result["condition_risk"] = np.clip(1 - (cond / 10), 0, 1)
    else:
        result["condition_risk"] = 0.5

    # Thickness risk
    if "remaining_thickness_mm" in result.columns and "original_thickness_mm" in result.columns:
        remain = result["remaining_thickness_mm"].fillna(0)
        orig = result["original_thickness_mm"].fillna(1).replace(0, 1)
        result["thickness_risk"] = np.clip(1 - (remain / orig), 0, 1)
    else:
        result["thickness_risk"] = 0.5

    # Composite risk score
    result["risk_score"] = (
        result["age_risk"] * 0.25 +
        result["corrosion_risk"] * 0.30 +
        result["condition_risk"] * 0.25 +
        result["thickness_risk"] * 0.20
    )

    # Risk category
    result["risk_category"] = pd.cut(
        result["risk_score"],
        bins=[0, 0.3, 0.5, 0.7, 1.0],
        labels=["Low", "Medium", "High", "Critical"],
        include_lowest=True,
    ).astype(str)

    return result


def compute_financial_exposure(df: pd.DataFrame) -> dict:
    """Calculate total financial exposure metrics."""
    if df.empty:
        return {
            "total_replacement": 0,
            "total_loans": 0,
            "total_insurance": 0,
            "avg_risk": 0,
            "high_risk_count": 0,
            "critical_count": 0,
        }

    replacement = df["replacement_cost_M"].sum() if "replacement_cost_M" in df.columns else 0
    loans = df["loan_outstanding_M"].sum() if "loan_outstanding_M" in df.columns else 0
    insurance = df["insurance_premium_K_yr"].sum() if "insurance_premium_K_yr" in df.columns else 0
    avg_risk = df["risk_score"].mean() if "risk_score" in df.columns else 0

    high_risk = len(df[df["risk_score"] >= 0.6]) if "risk_score" in df.columns else 0
    critical = len(df[df["risk_score"] >= 0.8]) if "risk_score" in df.columns else 0

    return {
        "total_replacement": float(replacement),
        "total_loans": float(loans),
        "total_insurance": float(insurance),
        "avg_risk": float(avg_risk),
        "high_risk_count": int(high_risk),
        "critical_count": int(critical),
    }


def compute_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Compute Value at Risk for a return series."""
    clean = returns.dropna()
    if len(clean) < 10:
        return 0.0
    return float(np.percentile(clean, (1 - confidence) * 100))


def compute_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    """Compute Conditional Value at Risk (Expected Shortfall)."""
    clean = returns.dropna()
    if len(clean) < 10:
        return 0.0
    var = compute_var(clean, confidence)
    return float(clean[clean <= var].mean()) if len(clean[clean <= var]) > 0 else var


def failure_probability_analysis(failures_df: pd.DataFrame) -> dict:
    """Analyze failure patterns and probabilities."""
    if failures_df.empty:
        return {
            "by_mode": pd.DataFrame(),
            "by_severity": pd.DataFrame(),
            "by_material": pd.DataFrame(),
            "avg_loss_ratio": 0,
            "prediction_rate": 0,
        }

    by_mode = failures_df["failure_mode"].value_counts().reset_index()
    by_mode.columns = ["failure_mode", "count"]

    by_severity = failures_df["severity"].value_counts().reset_index()
    by_severity.columns = ["severity", "count"]

    by_material = failures_df["material"].value_counts().head(10).reset_index()
    by_material.columns = ["material", "count"]

    avg_loss = float(failures_df["loss_ratio"].mean()) if "loss_ratio" in failures_df.columns else 0
    pred_rate = float(failures_df["was_predicted"].mean()) if "was_predicted" in failures_df.columns else 0

    return {
        "by_mode": by_mode,
        "by_severity": by_severity,
        "by_material": by_material,
        "avg_loss_ratio": avg_loss,
        "prediction_rate": pred_rate,
    }
