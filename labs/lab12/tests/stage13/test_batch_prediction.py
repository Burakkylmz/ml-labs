from pathlib import Path

import pytest

from inference.contracts import FeatureSchemaError
from inference.predictor import FreightCostPredictor


@pytest.fixture()
def predictor(bundle_dir: Path, allowed_root: Path):
    return FreightCostPredictor.load(bundle_dir, allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="M04-T003")


def test_empty_batch_returns_empty_list(predictor):
    assert predictor.predict_batch([]) == []


def test_batch_preserves_order_and_count(predictor, valid_shipment):
    shipments = [dict(valid_shipment, Line_Item_Qty_Sum=float(q)) for q in (100, 500, 900, 1500)]
    results = predictor.predict_batch(shipments)
    assert len(results) == len(shipments)
    # Larger quantity should not decrease the ordering we fed in -- verify alignment via single-call parity.
    singles = [predictor.predict_one(s).prediction_usd for s in shipments]
    assert [r.prediction_usd for r in results] == singles


def test_batch_size_limit_enforced(predictor, valid_shipment):
    oversized_batch = [dict(valid_shipment) for _ in range(predictor.max_batch_size + 1)]
    with pytest.raises(FeatureSchemaError, match="BATCH_SIZE_EXCEEDED"):
        predictor.predict_batch(oversized_batch)


def test_batch_rejects_whole_batch_on_one_invalid_row(predictor, valid_shipment):
    bad_shipment = dict(valid_shipment)
    del bad_shipment["Country"]
    with pytest.raises(FeatureSchemaError):
        predictor.predict_batch([valid_shipment, bad_shipment])


def test_single_vs_batch_numerical_equivalence(predictor, valid_shipment):
    single_result = predictor.predict_one(valid_shipment)
    batch_result = predictor.predict_batch([valid_shipment])[0]
    assert single_result.prediction_usd == batch_result.prediction_usd
