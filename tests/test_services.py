"""
MatRisk AI - Unit Tests
Basic tests for risk calculations and data processing.
"""

import unittest
import pandas as pd
import numpy as np
from services.risk_service import compute_var, compute_cvar, compute_infrastructure_risk
from services.simulation_service import monte_carlo_price


class TestRiskService(unittest.TestCase):
    def test_var_calculation(self):
        returns = pd.Series([-0.05, -0.04, -0.03, -0.02, -0.01, 0, 0.01, 0.02, 0.03, 0.04, 0.05])
        var_95 = compute_var(returns, 0.95)
        self.assertLess(var_95, 0)


    def test_infrastructure_risk_empty(self):
        df = pd.DataFrame()
        result = compute_infrastructure_risk(df)
        self.assertTrue(result.empty)

    def test_infrastructure_risk_scoring(self):
        df = pd.DataFrame({
            "age_years": [10, 90],
            "design_life_years": [100, 100],
            "condition_rating": [9, 2]
        })
        result = compute_infrastructure_risk(df)
        self.assertIn("risk_score", result.columns)
        self.assertGreater(result.iloc[1]["risk_score"], result.iloc[0]["risk_score"])


class TestSimulationService(unittest.TestCase):
    def test_monte_carlo_dimensions(self):
        days = 10
        sims = 50
        result = monte_carlo_price(100, 0.05, 0.2, days=days, simulations=sims)
        self.assertEqual(result["paths"].shape, (days, sims))
        self.assertGreater(result["prob_up"], 0)
        self.assertLess(result["prob_up"], 1)


if __name__ == "__main__":
    unittest.main()
