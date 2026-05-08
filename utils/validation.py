"""
MatRisk AI - Schema Validation Utility
Defines expected schemas and provides validation functions for datasets.
"""

import pandas as pd
from utils.constants import (
    MAT_COLS, CPRICE_COLS, COMM_COLS, INFRA_COLS,
    INFRA_SMALL_COLS, FAIL_COLS, ESG_COLS
)


def validate_schema(df: pd.DataFrame, dataset_name: str) -> dict:
    """
    Validate that the DataFrame contains required columns for the dataset.
    Returns a dict with 'valid' (bool) and 'missing' (list).
    """
    if df.empty:
        return {"valid": False, "missing": ["All columns (empty DataFrame)"]}

    # Mapping of dataset names to their column constants
    schema_map = {
        "materials": MAT_COLS.values(),
        "commodity_prices": CPRICE_COLS.values(),
        "commodities": COMM_COLS.values(),
        "infrastructure_assets": INFRA_COLS.values(),
        "infrastructure": INFRA_SMALL_COLS.values(),
        "historical_failures": FAIL_COLS.values(),
        "esg": ESG_COLS.values(),
    }

    expected_cols = schema_map.get(dataset_name)
    if expected_cols is None:
        return {"valid": True, "missing": []}  # Unknown dataset, skip validation

    missing = [col for col in expected_cols if col not in df.columns]
    
    return {
        "valid": len(missing) == 0,
        "missing": missing,
        "unexpected": [col for col in df.columns if col not in expected_cols]
    }


def perform_system_check() -> dict:
    """Run validation across all primary datasets and return a status report."""
    from utils.data_loader import (
        load_materials, load_commodity_prices, load_commodities,
        load_infrastructure_assets, load_infrastructure,
        load_historical_failures, load_esg
    )
    
    loaders = {
        "materials": load_materials,
        "commodity_prices": load_commodity_prices,
        "commodities": load_commodities,
        "infrastructure_assets": load_infrastructure_assets,
        "infrastructure": load_infrastructure,
        "historical_failures": load_historical_failures,
        "esg": load_esg,
    }
    
    report = {}
    for name, loader in loaders.items():
        try:
            df = loader()
            report[name] = validate_schema(df, name)
        except Exception as e:
            report[name] = {"valid": False, "error": str(e)}
            
    return report
