from pathlib import Path

import pytest

from inference.predictor import FreightCostPredictor


@pytest.fixture()
def predictor(bundle_dir: Path, allowed_root: Path):
    return FreightCostPredictor.load(bundle_dir, allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="M04-T003")


def test_uncertainty_status_is_disabled_by_default(predictor, valid_shipment):
    result = predictor.predict_one(valid_shipment)
    assert result.uncertainty_status == "disabled"


def test_requesting_interval_does_not_return_bounds(predictor, valid_shipment):
    result = predictor.predict_one(valid_shipment, request_interval=True)
    result_dict = result.to_dict()
    assert "interval_lower_usd" not in result_dict
    assert "interval_upper_usd" not in result_dict
    assert result.uncertainty_status == "disabled"


def test_requesting_interval_flags_but_does_not_block_point_prediction(predictor, valid_shipment):
    result = predictor.predict_one(valid_shipment, request_interval=True)
    assert "INTERVAL_NOT_APPROVED" in result.risk_flags
    assert result.prediction_validity == "valid"
    assert result.prediction_usd is not None


def test_batch_interval_policy_consistent_with_single(predictor, valid_shipment):
    results = predictor.predict_batch([valid_shipment, valid_shipment], request_interval=True)
    for r in results:
        assert "INTERVAL_NOT_APPROVED" in r.risk_flags
        assert r.uncertainty_status == "disabled"
