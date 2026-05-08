"""
MatRisk AI - ML Service
Machine learning models for material property prediction and analysis.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score
import streamlit as st


@st.cache_resource
def _get_label_encoder():
    return LabelEncoder()


def predict_material_stability(df: pd.DataFrame) -> dict:
    """Train a classifier to predict material stability (is_stable)."""
    if df.empty:
        return {"accuracy": 0, "predictions": [], "model": None}

    feature_cols = [
        "formation_energy_per_atom_eV", "energy_above_hull_eV",
        "band_gap_eV", "bulk_modulus_GPa", "shear_modulus_GPa",
        "poisson_ratio", "density_g_cm3", "melting_point_K",
    ]
    target = "is_stable"

    available = [c for c in feature_cols if c in df.columns]
    if len(available) < 3 or target not in df.columns:
        return {"accuracy": 0, "predictions": [], "model": None}

    work = df[available + [target]].dropna().reset_index(drop=True)
    if len(work) < 20:
        return {"accuracy": 0, "predictions": [], "model": None}

    X = work[available].values
    y = work[target].astype(int).values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train_s, y_train)

    preds = model.predict(X_test_s)
    acc = accuracy_score(y_test, preds)

    importances = dict(zip(available, model.feature_importances_))

    return {
        "accuracy": float(acc),
        "predictions": preds.tolist(),
        "y_test": y_test.tolist(),
        "feature_importances": importances,
        "model": model,
        "scaler": scaler,
        "features": available,
    }


def predict_material_property(df: pd.DataFrame, target_col: str) -> dict:
    """Train a regressor for a given material property."""
    if df.empty:
        return {"r2": 0, "mae": 0, "model": None}

    feature_cols = [
        "n_elements", "formation_energy_per_atom_eV", "energy_above_hull_eV",
        "band_gap_eV", "density_g_cm3", "nsites", "volume_A3",
    ]

    available = [c for c in feature_cols if c in df.columns and c != target_col]
    if len(available) < 2 or target_col not in df.columns:
        return {"r2": 0, "mae": 0, "model": None}

    work = df[available + [target_col]].dropna().reset_index(drop=True)
    if len(work) < 20:
        return {"r2": 0, "mae": 0, "model": None}

    X = work[available].values
    y = work[target_col].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train_s, y_train)

    preds = model.predict(X_test_s)
    r2 = r2_score(y_test, preds)
    mae = mean_absolute_error(y_test, preds)

    importances = dict(zip(available, model.feature_importances_))

    return {
        "r2": float(r2),
        "mae": float(mae),
        "predictions": preds.tolist(),
        "y_test": y_test.tolist(),
        "feature_importances": importances,
        "model": model,
        "scaler": scaler,
        "features": available,
    }


def predict_commodity_trend(df: pd.DataFrame) -> dict:
    """Simple commodity trend prediction using price momentum."""
    if df.empty:
        return {"predictions": pd.DataFrame()}

    results = []
    for commodity in df["commodity"].unique():
        cdf = df[df["commodity"] == commodity].sort_values("date").tail(30)
        if len(cdf) < 5:
            continue

        close = cdf["close"].values
        avg_return = np.mean(np.diff(close) / close[:-1]) if len(close) > 1 else 0.0

        last_price = float(close[-1])
        vol = float(cdf["close"].std() / cdf["close"].mean()) if cdf["close"].mean() != 0 else 0

        if avg_return > 0.005:
            trend = "Bullish"
        elif avg_return < -0.005:
            trend = "Bearish"
        else:
            trend = "Neutral"

        rsi_val = float(cdf["rsi_14"].dropna().iloc[-1]) if "rsi_14" in cdf.columns and len(cdf["rsi_14"].dropna()) > 0 else 50.0

        results.append({
            "commodity": commodity,
            "last_price": last_price,
            "avg_daily_return": float(avg_return),
            "volatility": vol,
            "trend": trend,
            "rsi": rsi_val,
            "signal": "Buy" if trend == "Bullish" and rsi_val < 70 else ("Sell" if trend == "Bearish" and rsi_val > 30 else "Hold"),
        })

    return {"predictions": pd.DataFrame(results)}


def generate_ai_insights(materials_df: pd.DataFrame, infra_df: pd.DataFrame,
                         failures_df: pd.DataFrame, esg_df: pd.DataFrame) -> list:
    """Generate AI-driven insights from cross-domain analysis."""
    insights = []

    # Material insights
    if not materials_df.empty and "is_stable" in materials_df.columns:
        stability_rate = materials_df["is_stable"].mean()
        insights.append({
            "category": "Materials",
            "icon": "🧪",
            "title": "Material Stability Overview",
            "detail": f"{stability_rate*100:.1f}% of materials in the database are thermodynamically stable.",
            "severity": "info" if stability_rate > 0.5 else "warning",
        })

    if not materials_df.empty and "band_gap_eV" in materials_df.columns:
        metals = materials_df[materials_df["band_gap_eV"] == 0]
        pct_metals = len(metals) / len(materials_df) * 100 if len(materials_df) > 0 else 0
        insights.append({
            "category": "Materials",
            "icon": "⚡",
            "title": "Metallic Material Distribution",
            "detail": f"{pct_metals:.1f}% of materials are metallic (zero band gap), relevant for structural applications.",
            "severity": "info",
        })

    # Infrastructure insights
    if not infra_df.empty and "condition_rating" in infra_df.columns:
        avg_condition = infra_df["condition_rating"].mean()
        poor_count = len(infra_df[infra_df["condition_rating"] < 5])
        insights.append({
            "category": "Infrastructure",
            "icon": "🏗️",
            "title": "Asset Condition Alert",
            "detail": f"Average condition rating: {avg_condition:.1f}/10. {poor_count} assets rated below 5 require attention.",
            "severity": "warning" if avg_condition < 6 else "info",
        })

    # Failure insights
    if not failures_df.empty and "failure_mode" in failures_df.columns:
        top_mode = failures_df["failure_mode"].value_counts().index[0] if len(failures_df) > 0 else "N/A"
        total_loss = failures_df["repair_cost_USD"].sum() if "repair_cost_USD" in failures_df.columns else 0
        insights.append({
            "category": "Risk",
            "icon": "⚠️",
            "title": "Failure Pattern Analysis",
            "detail": f"Top failure mode: {top_mode}. Total historical repair costs: ${total_loss:,.0f}.",
            "severity": "danger",
        })

    # ESG insights
    if not esg_df.empty and "sustainability_score" in esg_df.columns:
        best = esg_df.loc[esg_df["sustainability_score"].idxmax()]
        worst = esg_df.loc[esg_df["sustainability_score"].idxmin()]
        insights.append({
            "category": "ESG",
            "icon": "🌱",
            "title": "Sustainability Leaders & Laggards",
            "detail": f"Best: {best.get('material', 'N/A')} (score: {best.get('sustainability_score', 0):.2f}). "
                      f"Worst: {worst.get('material', 'N/A')} (score: {worst.get('sustainability_score', 0):.2f}).",
            "severity": "info",
        })

    if not insights:
        insights.append({
            "category": "System",
            "icon": "ℹ️",
            "title": "Awaiting Data",
            "detail": "Load datasets to generate AI-powered insights.",
            "severity": "info",
        })

    return insights
