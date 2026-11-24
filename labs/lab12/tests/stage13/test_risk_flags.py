from pathlib import Path

import pytest

from inference.contracts import RISK_FLAG_PREDICTION_OUTSIDE_REFERENCE_RANGE, RISK_FLAG_UNVERIFIED_FEATURE_AVAILABILITY
from inference.predictor import FreightCostPredictor
from inference.risk_flags import evaluate_prediction_flags, interval_requested_flag, structural_flags


@pytest.fixture()
def predictor(bundle_dir: Path, allowed_root: Path):
    return FreightCostPredictor.load(bundle_dir, allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="M04-T003")


def test_structural_flag_always_present(predictor, valid_shipment):
    result = predictor.predict_one(valid_shipment)
    assert RISK_FLAG_UNVERIFIED_FEATURE_AVAILABILITY in result.risk_flags


def test_unknown_category_triggers_flag(predictor, valid_shipment):
    shipment = dict(valid_shipment, Country="Atlantis")
    result = predictor.predict_one(shipment)
    assert "UNKNOWN_CATEGORY" in result.risk_flags


def test_prediction_outside_reference_range_flag_triggers_above_max():
    flags = evaluate_prediction_flags(prediction_usd=1_000_000.0, reference_min_usd=0.0, reference_max_usd=100_000.0)
    assert RISK_FLAG_PREDICTION_OUTSIDE_REFERENCE_RANGE in flags


def test_prediction_outside_reference_range_flag_absent_within_range():
    flags = evaluate_prediction_flags(prediction_usd=5000.0, reference_min_usd=0.0, reference_max_usd=100_000.0)
    assert flags == []


def test_interval_requested_flag_only_when_requested():
    assert interval_requested_flag(True) == ["INTERVAL_NOT_APPROVED"]
    assert interval_requested_flag(False) == []


def test_structural_flags_is_deterministic():
    assert structural_flags() == structural_flags()
