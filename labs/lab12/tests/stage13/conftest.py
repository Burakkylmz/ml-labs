"""Shared fixtures for Stage 13 inference package tests.

These tests use a small SYNTHETIC pipeline (not the real Stage 11 frozen
model) so they run fast and do not depend on the real dataset being
present. The real frozen-model identity/parity checks against Stage 11/12
artifacts are performed separately, inside the Stage 13 notebook, against
the actual trained bundle.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

PACKAGE_ROOT = Path(__file__).resolve().parents[2]  # labs/lab12
sys.path.insert(0, str(PACKAGE_ROOT))

from inference.artifact_store import write_bundle  # noqa: E402

NUMERIC = ("Line_Item_Qty_Sum", "Line_Item_Value_Sum")
CATEGORICAL = ("Shipment_Mode", "INCO_Term", "Country", "Product_Group")


def _build_fitted_pipeline(seed: int = 42):
    rng = np.random.default_rng(seed)
    n = 300
    df = pd.DataFrame({
        "Line_Item_Qty_Sum": rng.integers(10, 10000, n).astype(float),
        "Line_Item_Value_Sum": rng.uniform(100, 100000, n),
        "Shipment_Mode": rng.choice(["Air", "Ocean", "Truck"], n),
        "INCO_Term": rng.choice(["EXW", "DDP", "CIP"], n),
        "Country": rng.choice(["Nigeria", "Kenya", "Uganda"], n),
        "Product_Group": rng.choice(["ARV", "HRDT"], n),
    })
    y = (df["Line_Item_Value_Sum"] * 0.1 + df["Line_Item_Qty_Sum"] * 0.01 + rng.normal(0, 50, n)).clip(lower=1.0)

    preprocessor = ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median"))]), list(NUMERIC)),
        ("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value="Missing")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", min_frequency=10, sparse_output=False)),
        ]), list(CATEGORICAL)),
    ])
    pipeline = Pipeline([("preprocessor", preprocessor), ("model", ExtraTreesRegressor(n_estimators=50, random_state=seed))])
    pipeline.fit(df, y)
    return pipeline, df, y


@pytest.fixture(scope="session")
def fitted_pipeline_and_data():
    return _build_fitted_pipeline()


@pytest.fixture()
def bundle_dir(tmp_path, fitted_pipeline_and_data):
    pipeline, _df, y = fitted_pipeline_and_data
    bundle_version_dir = tmp_path / "bundle" / "v1"
    manifest_fields = {
        "model_id": "M04", "trial_id": "M04-T003", "artifact_version": "v1", "feature_schema_version": "test-v1",
        "feature_schema_inline": {"numeric": list(NUMERIC), "categorical": list(CATEGORICAL)},
        "reference_stats": {"min_usd": float(y.min()), "max_usd": float(y.max())},
        "environment": {"python_version": sys.version.split()[0], "sklearn_version": sklearn.__version__},
    }
    write_bundle(
        fitted_pipeline=pipeline, bundle_version_dir=bundle_version_dir, manifest_fields=manifest_fields,
        feature_schema={"numeric": list(NUMERIC), "categorical": list(CATEGORICAL)}, preprocessing_schema={}, model_config={},
        environment=manifest_fields["environment"], reference_predictions={},
    )
    return bundle_version_dir


@pytest.fixture()
def allowed_root(tmp_path):
    return tmp_path


@pytest.fixture()
def valid_shipment():
    return {
        "Line_Item_Qty_Sum": 500.0, "Line_Item_Value_Sum": 20000.0,
        "Shipment_Mode": "Air", "INCO_Term": "EXW", "Country": "Nigeria", "Product_Group": "ARV",
    }
