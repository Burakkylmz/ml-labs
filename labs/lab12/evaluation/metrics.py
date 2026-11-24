"""Frozen metric formulas, recovered from stage08_baseline_evaluation.md
and stage11_external_validation_results.md. See contracts.py for the
formula notes surfaced in the protocol doc; this module is the single
implementation both the protocol doc and the runner refer to.
"""

from __future__ import annotations

import numpy as np

from .contracts import HIGH_COST_THRESHOLD_USD


def mae(actual: np.ndarray, prediction: np.ndarray) -> float:
    return float(np.mean(np.abs(actual - prediction)))


def rmse(actual: np.ndarray, prediction: np.ndarray) -> float:
    return float(np.sqrt(np.mean((actual - prediction) ** 2)))


def median_ae(actual: np.ndarray, prediction: np.ndarray) -> float:
    return float(np.median(np.abs(actual - prediction)))


def wape(actual: np.ndarray, prediction: np.ndarray) -> float:
    denominator = np.sum(np.abs(actual))
    if denominator == 0:
        raise ValueError("WAPE is undefined when sum(|actual|) == 0")
    return float(100.0 * np.sum(np.abs(actual - prediction)) / denominator)


def bias(actual: np.ndarray, prediction: np.ndarray) -> float:
    """Mean(prediction - actual); negative = systematic underprediction."""
    return float(np.mean(prediction - actual))


def p90_ae(actual: np.ndarray, prediction: np.ndarray) -> float:
    return float(np.percentile(np.abs(actual - prediction), 90))


def p95_ae(actual: np.ndarray, prediction: np.ndarray) -> float:
    return float(np.percentile(np.abs(actual - prediction), 95))


def prediction_validity_rate(validity_flags: list[str]) -> float:
    if len(validity_flags) == 0:
        raise ValueError("prediction_validity_rate is undefined for an empty evaluation set")
    n_valid = sum(1 for flag in validity_flags if flag == "valid")
    return float(100.0 * n_valid / len(validity_flags))


def negative_prediction_count(raw_predictions: np.ndarray) -> int:
    return int(np.sum(raw_predictions < 0))


def high_cost_mask(actual: np.ndarray, threshold_usd: float = HIGH_COST_THRESHOLD_USD) -> np.ndarray:
    return actual >= threshold_usd


def high_cost_mae(actual: np.ndarray, prediction: np.ndarray, threshold_usd: float = HIGH_COST_THRESHOLD_USD) -> float | None:
    mask = high_cost_mask(actual, threshold_usd)
    if not mask.any():
        return None
    return mae(actual[mask], prediction[mask])


def high_cost_underprediction_rate(actual: np.ndarray, prediction: np.ndarray, threshold_usd: float = HIGH_COST_THRESHOLD_USD) -> float | None:
    mask = high_cost_mask(actual, threshold_usd)
    if not mask.any():
        return None
    underpredicted = prediction[mask] < actual[mask]
    return float(100.0 * np.sum(underpredicted) / mask.sum())


def compute_all_metrics(actual: np.ndarray, prediction: np.ndarray, validity_flags: list[str], raw_predictions: np.ndarray) -> dict[str, float | int | None]:
    """All frozen metrics in one call, over an already-aligned, eligible
    evaluation set. `actual`/`prediction` must only include valid-prediction
    rows (invalid rows are excluded from error metrics but counted in
    `prediction_validity_rate`, which uses the full `validity_flags`)."""
    return {
        "MAE": mae(actual, prediction),
        "RMSE": rmse(actual, prediction),
        "Median_AE": median_ae(actual, prediction),
        "WAPE": wape(actual, prediction),
        "Bias": bias(actual, prediction),
        "P90_AE": p90_ae(actual, prediction),
        "P95_AE": p95_ae(actual, prediction),
        "Prediction_Validity_Rate": prediction_validity_rate(validity_flags),
        "Negative_Prediction_Count": negative_prediction_count(raw_predictions),
        "High_Cost_MAE": high_cost_mae(actual, prediction),
        "High_Cost_Underprediction_Rate": high_cost_underprediction_rate(actual, prediction),
    }
