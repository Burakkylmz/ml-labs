import numpy as np
import pytest

from evaluation import metrics


def test_mae_and_rmse():
    actual = np.array([100.0, 200.0, 300.0])
    pred = np.array([110.0, 180.0, 310.0])
    assert metrics.mae(actual, pred) == pytest.approx((10 + 20 + 10) / 3)
    assert metrics.rmse(actual, pred) == pytest.approx(np.sqrt((100 + 400 + 100) / 3))


def test_wape_and_bias():
    actual = np.array([100.0, 200.0, 300.0])
    pred = np.array([110.0, 180.0, 310.0])
    assert metrics.wape(actual, pred) == pytest.approx(100 * 40 / 600)
    assert metrics.bias(actual, pred) == pytest.approx(((110 - 100) + (180 - 200) + (310 - 300)) / 3)


def test_wape_undefined_for_zero_actual_sum():
    with pytest.raises(ValueError):
        metrics.wape(np.array([0.0, 0.0]), np.array([1.0, 2.0]))


def test_median_p90_p95_absolute_error():
    actual = np.array([0.0] * 10)
    pred = np.array([float(i) for i in range(1, 11)])  # abs errors 1..10
    assert metrics.median_ae(actual, pred) == pytest.approx(5.5)
    assert metrics.p90_ae(actual, pred) == pytest.approx(np.percentile(np.arange(1, 11), 90))
    assert metrics.p95_ae(actual, pred) == pytest.approx(np.percentile(np.arange(1, 11), 95))


def test_high_cost_threshold_is_the_frozen_constant_not_recomputed():
    """High-cost segmentation must use the FROZEN Stage 11 threshold, never
    a threshold derived from the data being scored (no data leakage into
    the segment definition itself)."""
    actual = np.array([10.0, 23897.32, 50000.0])
    mask = metrics.high_cost_mask(actual)
    assert mask.tolist() == [False, True, True]
    assert metrics.HIGH_COST_THRESHOLD_USD == 23897.32


def test_high_cost_mae_and_underprediction_rate():
    actual = np.array([30000.0, 40000.0])
    pred = np.array([25000.0, 45000.0])  # first underpredicts, second overpredicts
    assert metrics.high_cost_mae(actual, pred) == pytest.approx((5000 + 5000) / 2)
    assert metrics.high_cost_underprediction_rate(actual, pred) == pytest.approx(50.0)


def test_high_cost_metrics_none_when_segment_empty():
    actual = np.array([10.0, 20.0])
    pred = np.array([11.0, 19.0])
    assert metrics.high_cost_mae(actual, pred) is None
    assert metrics.high_cost_underprediction_rate(actual, pred) is None


def test_prediction_validity_rate():
    flags = ["valid", "valid", "invalid", "valid"]
    assert metrics.prediction_validity_rate(flags) == pytest.approx(75.0)


def test_prediction_validity_rate_empty_raises():
    with pytest.raises(ValueError):
        metrics.prediction_validity_rate([])


def test_negative_prediction_count():
    raw = np.array([-5.0, 10.0, -0.01, 20.0])
    assert metrics.negative_prediction_count(raw) == 2


def test_compute_all_metrics_excludes_invalid_rows_from_error_metrics_but_counts_them_in_validity_rate():
    """Invalid (e.g. negative-clipped-to-invalid) predictions must not pollute
    MAE/RMSE/etc, but ARE counted in Prediction_Validity_Rate -- the caller
    (runner.py) passes only the valid-masked actual/prediction pair plus the
    FULL validity_flags list, by design."""
    actual_valid_only = np.array([100.0, 200.0])
    pred_valid_only = np.array([110.0, 190.0])
    all_validity_flags = ["valid", "valid", "invalid"]
    raw_predictions = np.array([110.0, 190.0, -50.0])

    result = metrics.compute_all_metrics(actual_valid_only, pred_valid_only, all_validity_flags, raw_predictions)
    assert result["MAE"] == pytest.approx(10.0)
    assert result["Prediction_Validity_Rate"] == pytest.approx(200 / 3)
    assert result["Negative_Prediction_Count"] == 1
