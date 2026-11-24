"""Deterministic, training-only-diagnostics-based risk flags.

Every rule here is computed from statistics of the full-development
training population (never from 2014/2015 labels) or from the structural
state of the input itself. None of these flags are a calibrated
uncertainty measure -- they are observable risk indicators only (see
stage13_explainability_risk_policy.md).
"""

from __future__ import annotations

from .contracts import (
    RISK_FLAG_INTERVAL_NOT_APPROVED,
    RISK_FLAG_INVALID_PREDICTION_DOMAIN,
    RISK_FLAG_PREDICTION_OUTSIDE_REFERENCE_RANGE,
    RISK_FLAG_UNVERIFIED_FEATURE_AVAILABILITY,
)


def evaluate_prediction_flags(prediction_usd: float | None, reference_min_usd: float, reference_max_usd: float) -> list[str]:
    """Flags derived from the prediction value and training-only reference range."""
    flags: list[str] = []
    if prediction_usd is None:
        flags.append(RISK_FLAG_INVALID_PREDICTION_DOMAIN)
        return flags
    if prediction_usd < reference_min_usd or prediction_usd > reference_max_usd:
        flags.append(RISK_FLAG_PREDICTION_OUTSIDE_REFERENCE_RANGE)
    return flags


def structural_flags() -> list[str]:
    """Flags that apply to every prediction, regardless of input, as a standing disclosure.

    UNVERIFIED_FEATURE_AVAILABILITY: D-006 (Weight) and D-007 (label timestamp) remain
    open/Conditional -- the engineered Minimal Core features' prediction-time
    availability has never been independently verified against a real pre-shipment
    data feed. This is disclosed on every prediction, not computed per-input.
    """
    return [RISK_FLAG_UNVERIFIED_FEATURE_AVAILABILITY]


def interval_requested_flag(interval_requested: bool) -> list[str]:
    if interval_requested:
        return [RISK_FLAG_INTERVAL_NOT_APPROVED]
    return []
