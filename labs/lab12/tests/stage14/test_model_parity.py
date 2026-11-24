"""stage14_api_deployment_contract.md Section 17: the API must return
`FreightCostPredictor.predict_one()`'s direct output, with no additional
rounding or transformation."""

from pathlib import Path

from api.config import BUNDLE_ROOT, BUNDLE_VERSION_DIR, EXPECTED_MODEL_ID, EXPECTED_TRIAL_ID
from inference.predictor import FreightCostPredictor

PREDICTION_TOLERANCE_USD = 1e-6


def _assert_results_match(api_result: dict, direct_result: dict) -> None:
    """Tolerance-based on `prediction_usd` only (D-154 precedent): two independently
    loaded instances of the same immutable bundle can differ by ~1e-13 USD under
    ExtraTrees' `n_jobs=2` thread-order-dependent summation -- see stage14 D-162.
    Every other field must match exactly."""
    assert api_result.keys() == direct_result.keys()
    for key in api_result:
        if key == "prediction_usd" and api_result[key] is not None and direct_result[key] is not None:
            assert abs(api_result[key] - direct_result[key]) < PREDICTION_TOLERANCE_USD
        else:
            assert api_result[key] == direct_result[key]


def test_api_prediction_is_bitwise_identical_to_direct_predictor_call(client, valid_shipment):
    direct_predictor = FreightCostPredictor.load(
        bundle_dir=BUNDLE_VERSION_DIR, allowed_root=BUNDLE_ROOT,
        expected_model_id=EXPECTED_MODEL_ID, expected_trial_id=EXPECTED_TRIAL_ID,
    )
    direct_result = direct_predictor.predict_one(valid_shipment).to_dict()
    api_result = client.post("/predict", json=valid_shipment).json()
    _assert_results_match(api_result, direct_result)


def test_api_batch_matches_direct_predictor_batch(valid_shipment, client):
    direct_predictor = FreightCostPredictor.load(
        bundle_dir=BUNDLE_VERSION_DIR, allowed_root=BUNDLE_ROOT,
        expected_model_id=EXPECTED_MODEL_ID, expected_trial_id=EXPECTED_TRIAL_ID,
    )
    shipments = [dict(valid_shipment, Line_Item_Qty_Sum=float(q)) for q in (10, 1000, 9000)]
    direct_results = [r.to_dict() for r in direct_predictor.predict_batch(shipments)]
    api_results = client.post("/predict/batch", json=shipments).json()
    for api_result, direct_result in zip(api_results, direct_results):
        _assert_results_match(api_result, direct_result)


def test_bundle_version_dir_is_the_real_stage13_bundle():
    assert BUNDLE_VERSION_DIR == Path(BUNDLE_ROOT) / "v1"
    assert (BUNDLE_VERSION_DIR / "model.joblib").exists()
    assert (BUNDLE_VERSION_DIR / "manifest.json").exists()
