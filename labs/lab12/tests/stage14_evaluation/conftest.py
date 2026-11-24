"""Shared synthetic fixtures for Stage 14 Phase B preparation tests.

Every fixture here is FABRICATED -- small, synthetic row-level data shaped
like the real dataset's columns, never the real dataset itself, and never
anything from 2015. This mirrors Stage 13's `tests/stage13/conftest.py`
policy exactly (synthetic pipeline, not the real frozen model).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]  # labs/lab12
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

RAW_COLUMNS = ["ASN/DN #", "Freight Cost (USD)", "Shipment Mode", "Vendor INCO Term", "Country", "Product Group", "Line Item Quantity", "Line Item Value"]


@pytest.fixture()
def synthetic_raw_df() -> pd.DataFrame:
    """8 shipment groups: clean single-anchor eligible shipments, one
    reference-only (no numeric row, ineligible), and one ambiguous
    (two numeric rows, ineligible -- Stage 03.5's single-anchor rule)."""
    rows = [
        # SHIP-A: single row, clean numeric target, eligible
        ["SHIP-A", "1200.50", "Air", "EXW", "Kenya", "ARV", 100, 5000],
        # SHIP-B: two line items, one numeric anchor + a sibling non-numeric row, eligible
        ["SHIP-B", "3400.00", "Ocean", "FCA", "Nigeria", "HRDT", 50, 8000],
        ["SHIP-B", "See ASN/DN-SHIP-B (ID#:1)", "Ocean", "FCA", "Nigeria", "HRDT", 30, 2000],
        # SHIP-C: reference-only, no numeric anchor at all -- ineligible
        ["SHIP-C", "See ASN/DN-SHIP-A (ID#:1)", "Truck", "DDP", "Uganda", "ARV", 20, 1000],
        # SHIP-D: ambiguous, two numeric rows -- ineligible (Stage 03.5 single-anchor rule)
        ["SHIP-D", "500.00", "Air", "EXW", "Kenya", "ARV", 10, 500],
        ["SHIP-D", "600.00", "Air", "EXW", "Kenya", "ARV", 10, 500],
        # SHIP-E: clean, high-cost (for high-cost segment tests)
        ["SHIP-E", "50000.00", "Air Charter", "CIP", "Nigeria", "ARV", 900, 90000],
        # SHIP-F: clean, mid-cost
        ["SHIP-F", "2000.00", "Truck", "EXW", "Kenya", "HRDT", 40, 3000],
        # SHIP-G: clean, low-cost
        ["SHIP-G", "300.00", "Ocean", "DDP", "Uganda", "ARV", 5, 200],
        # SHIP-H: clean, mid-cost, Air/EXW combo repeated for min_support testing
        ["SHIP-H", "1100.00", "Air", "EXW", "Kenya", "ARV", 90, 4800],
    ]
    return pd.DataFrame(rows, columns=RAW_COLUMNS)


@pytest.fixture()
def synthetic_split_manifest(tmp_path) -> Path:
    df = pd.DataFrame({
        "Shipment_Key": ["SHIP-A", "SHIP-B", "SHIP-E", "SHIP-F", "SHIP-H", "SHIP-G"],
        "Split": ["Train", "Train", "Train", "Train", "Train", "Protected_Test"],
    })
    path = tmp_path / "split_manifest.csv"
    df.to_csv(path, index=False)
    return path


@pytest.fixture()
def synthetic_dataset_csv(tmp_path, synthetic_raw_df) -> Path:
    path = tmp_path / "synthetic_dataset.csv"
    synthetic_raw_df.to_csv(path, index=False, encoding="latin-1")
    return path


@pytest.fixture()
def synthetic_model_bundle(tmp_path):
    """A tiny, fully synthetic fitted pipeline, written through the REAL
    Stage 13 `inference.artifact_store.write_bundle` (reused, not
    duplicated) and labeled M04/M04-T003 purely as test metadata -- this
    is the exact same pattern `tests/stage13/conftest.py` already uses for
    its own synthetic-pipeline tests."""
    import sys as _sys

    import numpy as np
    import sklearn
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import ExtraTreesRegressor
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder

    from inference.artifact_store import write_bundle

    numeric = ("Line_Item_Qty_Sum", "Line_Item_Value_Sum")
    categorical = ("Shipment_Mode", "INCO_Term", "Country", "Product_Group")

    rng = np.random.default_rng(7)
    n = 150
    df = pd.DataFrame({
        "Line_Item_Qty_Sum": rng.integers(10, 1000, n).astype(float),
        "Line_Item_Value_Sum": rng.uniform(100, 100000, n),
        "Shipment_Mode": rng.choice(["Air", "Ocean", "Truck"], n),
        "INCO_Term": rng.choice(["EXW", "DDP"], n),
        "Country": rng.choice(["Kenya", "Nigeria"], n),
        "Product_Group": rng.choice(["ARV", "HRDT"], n),
    })
    y = (df["Line_Item_Value_Sum"] * 0.1 + rng.normal(0, 50, n)).clip(lower=1.0)

    preprocessor = ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median"))]), list(numeric)),
        ("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value="Missing")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), list(categorical)),
    ])
    pipeline = Pipeline([("preprocessor", preprocessor), ("model", ExtraTreesRegressor(n_estimators=20, random_state=7))])
    pipeline.fit(df, y)

    bundle_version_dir = tmp_path / "synthetic_bundle" / "v1"
    manifest_fields = {
        "model_id": "M04", "trial_id": "M04-T003", "artifact_version": "v1", "feature_schema_version": "test-v1",
        "feature_schema_inline": {"numeric": list(numeric), "categorical": list(categorical)},
        "reference_stats": {"min_usd": float(y.min()), "max_usd": float(y.max())},
        "environment": {"python_version": _sys.version.split()[0], "sklearn_version": sklearn.__version__},
    }
    write_bundle(
        fitted_pipeline=pipeline, bundle_version_dir=bundle_version_dir, manifest_fields=manifest_fields,
        feature_schema={"numeric": list(numeric), "categorical": list(categorical)}, preprocessing_schema={}, model_config={},
        environment=manifest_fields["environment"], reference_predictions={},
    )
    return bundle_version_dir, bundle_version_dir.parent  # (bundle_dir, allowed_root)


@pytest.fixture()
def development_frame() -> pd.DataFrame:
    """A small, already-resolved development population (Target + Minimal
    Core features) -- bypasses the CSV/ETL layer for baseline-only tests."""
    rng = np.random.default_rng(42)
    n = 200
    modes = rng.choice(["Air", "Ocean", "Truck"], n)
    incoterms = rng.choice(["EXW", "DDP"], n)
    base = pd.Series(modes).map({"Air": 6000, "Ocean": 4000, "Truck": 3000}).to_numpy()
    target = base + rng.normal(0, 200, n)
    return pd.DataFrame({
        "Shipment_Key": [f"DEV-{i}" for i in range(n)],
        "Target": target,
        "Shipment_Mode": modes, "INCO_Term": incoterms,
        "Line_Item_Qty_Sum": rng.integers(10, 500, n).astype(float),
        "Line_Item_Value_Sum": rng.uniform(1000, 50000, n),
        "Country": rng.choice(["Kenya", "Nigeria"], n),
        "Product_Group": rng.choice(["ARV", "HRDT"], n),
    })
