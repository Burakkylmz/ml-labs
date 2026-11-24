from pathlib import Path

from inference.predictor import FreightCostPredictor


def test_in_memory_vs_reloaded_prediction_parity(fitted_pipeline_and_data, bundle_dir: Path, allowed_root: Path, valid_shipment):
    pipeline, _df, _y = fitted_pipeline_and_data
    import pandas as pd

    in_memory_pred = float(pipeline.predict(pd.DataFrame([valid_shipment]))[0])

    predictor = FreightCostPredictor.load(bundle_dir, allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="M04-T003")
    reloaded_result = predictor.predict_one(valid_shipment)

    assert abs(in_memory_pred - reloaded_result.prediction_usd) < 1e-6


def test_repeated_predictions_are_deterministic(bundle_dir: Path, allowed_root: Path, valid_shipment):
    predictor = FreightCostPredictor.load(bundle_dir, allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="M04-T003")
    results = [predictor.predict_one(valid_shipment).prediction_usd for _ in range(5)]
    assert len(set(results)) == 1


def test_fresh_predictor_instance_matches_original(bundle_dir: Path, allowed_root: Path, valid_shipment):
    predictor_a = FreightCostPredictor.load(bundle_dir, allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="M04-T003")
    predictor_b = FreightCostPredictor.load(bundle_dir, allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="M04-T003")
    assert predictor_a.predict_one(valid_shipment).prediction_usd == predictor_b.predict_one(valid_shipment).prediction_usd
