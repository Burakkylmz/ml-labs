"""Fixed, trusted bundle configuration for the Stage 14 API.

Per stage14_api_deployment_contract.md Section 15: the API must NOT accept
an arbitrary, user- or environment-supplied model path. ARTIFACT_ROOT and
BUNDLE_VERSION_DIR are hardcoded constants, not read from a request,
header, query parameter, or environment variable.
"""

from __future__ import annotations

from pathlib import Path

LAB12_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = LAB12_ROOT / "artifacts"
BUNDLE_ROOT = ARTIFACT_ROOT / "stage13_model_bundle"
BUNDLE_VERSION_DIR = BUNDLE_ROOT / "v1"

EXPECTED_MODEL_ID = "M04"
EXPECTED_TRIAL_ID = "M04-T003"

MAX_BATCH_SIZE = 100
MAX_BATCH_EXPLANATIONS = 10

# Fixed canary shipment used at startup to prove the loaded bundle produces
# a valid prediction before the service accepts traffic (readiness gate).
CANARY_SHIPMENT: dict[str, object] = {
    "Line_Item_Qty_Sum": 500.0,
    "Line_Item_Value_Sum": 20000.0,
    "Shipment_Mode": "Air",
    "INCO_Term": "EXW",
    "Country": "Nigeria",
    "Product_Group": "ARV",
}
