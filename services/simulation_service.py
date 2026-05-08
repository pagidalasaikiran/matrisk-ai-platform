"""
MatRisk AI - Simulation Service
Monte Carlo simulation and scenario analysis.
"""

import pandas as pd
import numpy as np


def monte_carlo_price(last_price: float, mu: float, sigma: float,
                      days: int = 252, simulations: int = 1000,
                      seed: int = 42) -> dict:
    """Run Monte Carlo price simulation using Geometric Brownian Motion."""
    np.random.seed(seed)

    dt = 1 / 252
    paths = np.zeros((days, simulations))
    paths[0] = last_price

    for t in range(1, days):
        z = np.random.standard_normal(simulations)
        paths[t] = paths[t - 1] * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z)

    final_prices = paths[-1]

    return {
        "paths": paths,
        "final_prices": final_prices,
        "mean_final": float(np.mean(final_prices)),
        "median_final": float(np.median(final_prices)),
        "std_final": float(np.std(final_prices)),
        "p5": float(np.percentile(final_prices, 5)),
        "p25": float(np.percentile(final_prices, 25)),
        "p75": float(np.percentile(final_prices, 75)),
        "p95": float(np.percentile(final_prices, 95)),
        "prob_up": float(np.mean(final_prices > last_price)),
    }


def portfolio_simulation(assets: list, weights: list,
                         returns_matrix: np.ndarray,
                         simulations: int = 5000, seed: int = 42) -> dict:
    """Simulate portfolio outcomes with given weights."""
    np.random.seed(seed)

    if len(assets) == 0 or returns_matrix.size == 0:
        return {"returns": [], "sharpe": 0, "var_95": 0}

    n_assets = len(assets)
    weights = np.array(weights)
    weights = weights / weights.sum()  # Normalize

    mean_returns = np.mean(returns_matrix, axis=0)
    cov_matrix = np.cov(returns_matrix.T)

    results = []
    for _ in range(simulations):
        rand_weights = np.random.dirichlet(np.ones(n_assets))
        port_return = np.dot(rand_weights, mean_returns) * 252
        port_vol = np.sqrt(np.dot(rand_weights.T, np.dot(cov_matrix * 252, rand_weights)))
        sharpe = port_return / port_vol if port_vol > 0 else 0
        results.append({
            "return": float(port_return),
            "volatility": float(port_vol),
            "sharpe": float(sharpe),
        })

    result_df = pd.DataFrame(results)

    return {
        "results": result_df,
        "optimal_sharpe": result_df.loc[result_df["sharpe"].idxmax()].to_dict() if len(result_df) > 0 else {},
        "min_vol": result_df.loc[result_df["volatility"].idxmin()].to_dict() if len(result_df) > 0 else {},
    }


def stress_test_scenario(base_value: float, scenarios: dict) -> pd.DataFrame:
    """Run stress test scenarios on a base value."""
    results = []
    for name, shock in scenarios.items():
        stressed = base_value * (1 + shock)
        change = stressed - base_value
        results.append({
            "scenario": name,
            "shock_pct": shock * 100,
            "base_value": base_value,
            "stressed_value": stressed,
            "change": change,
            "pct_change": shock * 100,
        })
    return pd.DataFrame(results)


def corrosion_simulation(initial_thickness: float, corrosion_rate: float,
                         years: int = 50, uncertainty: float = 0.2,
                         simulations: int = 500, seed: int = 42) -> dict:
    """Simulate corrosion degradation with uncertainty."""
    np.random.seed(seed)

    time = np.arange(0, years + 1)
    paths = np.zeros((years + 1, simulations))
    paths[0] = initial_thickness

    for t in range(1, years + 1):
        noise = np.random.normal(1, uncertainty, simulations)
        rate = corrosion_rate * noise
        paths[t] = np.maximum(paths[t - 1] - rate, 0)

    mean_path = np.mean(paths, axis=1)
    p5 = np.percentile(paths, 5, axis=1)
    p95 = np.percentile(paths, 95, axis=1)

    # Time to failure (thickness = 0)
    ttf = []
    for sim in range(simulations):
        zero_idx = np.where(paths[:, sim] <= 0)[0]
        if len(zero_idx) > 0:
            ttf.append(zero_idx[0])
        else:
            ttf.append(years)

    return {
        "time": time.tolist(),
        "mean_path": mean_path.tolist(),
        "p5": p5.tolist(),
        "p95": p95.tolist(),
        "avg_ttf": float(np.mean(ttf)),
        "median_ttf": float(np.median(ttf)),
        "prob_failure_10yr": float(np.mean(np.array(ttf) <= 10)),
        "prob_failure_25yr": float(np.mean(np.array(ttf) <= 25)),
    }
