from pathlib import Path

import pytest

from inference.contracts import FeatureSchemaError
from inference.predictor import FreightCostPredictor


@pytest.fixture()
def predictor(bundle_dir: Path, allowed_root: Path):
    return FreightCostPredictor.load(bundle_dir, allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="M04-T003")


def test_explain_false_by_default_returns_not_requested(predictor, valid_shipment):
    result = predictor.predict_one(valid_shipment)
    assert result.explanation_status == "not_requested"
    assert result.explanation is None


def test_explain_true_returns_available_explanation(predictor, valid_shipment):
    result = predictor.predict_one(valid_shipment, explain=True)
    assert result.explanation_status == "available"
    assert result.explanation["method"] == "tree_shap"
    assert result.explanation["background_policy"] == "tree_path_dependent"
    assert isinstance(result.explanation["feature_contributions"], list)
    assert len(result.explanation["feature_contributions"]) > 0


def test_shap_additivity_holds(predictor, valid_shipment):
    result = predictor.predict_one(valid_shipment, explain=True)
    assert result.explanation["additivity_valid"] is True
    assert result.explanation["additivity_diff_usd"] < 1.0


def test_explanation_batch_limit_enforced(predictor, valid_shipment):
    oversized = [dict(valid_shipment) for _ in range(predictor.max_batch_explanations + 1)]
    with pytest.raises(FeatureSchemaError, match="EXPLANATION_BATCH_LIMIT_EXCEEDED"):
        predictor.predict_batch(oversized, explain=True)


def test_feature_contributions_sum_close_to_prediction_minus_base(predictor, valid_shipment):
    result = predictor.predict_one(valid_shipment, explain=True)
    total_contribution = sum(c["signed_contribution_usd"] for c in result.explanation["feature_contributions"])
    reconstructed = result.explanation["base_value_usd"] + total_contribution
    assert abs(reconstructed - result.prediction_usd) < 1.0
