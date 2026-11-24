"""Technical acceptance classification -- ENGINEERING thresholds only, not
a business-approved SLA (master prompt Section 4; see
stage14_metric_baseline_contract.md Section 5 for the frozen rationale).

**Revised in the Stage 14 Pre-Unlock Audit (D-173):** the high-cost
sub-criterion no longer compares the model's 2015 rate against a FIXED
tolerance over the 2014 reference (89.93% + 10pp = 99.93% -- a ceiling so
close to 100% that it is nearly impossible to fail, since the metric is
bounded at 100% and both existing baselines already score exactly 100% on
2014). It is now a same-period, relative comparison against B4 for
gating, with the old 2014-referenced check kept as a separate, explicitly
non-gating MONITOR field.

Frozen BEFORE any 2015 access. Pure function, independently testable with
synthetic metric dicts -- never needs the gate, the loaders, or the real
model to be exercised.
"""

from __future__ import annotations

from typing import Any

from .contracts import (
    ACCEPTANCE_HIGH_COST_MONITOR_TOLERANCE_PP,
    ACCEPTANCE_MIN_IMPROVEMENT_VS_B4,
    ACCEPTANCE_MIN_VALIDITY_RATE_PCT,
    ACCEPTANCE_REFERENCE_HIGH_COST_UNDERPREDICTION_PCT,
)


def _high_cost_risk_monitor(model_metrics: dict[str, Any], b4_metrics: dict[str, Any]) -> dict[str, Any]:
    """Informational only -- NEVER used to gate the classification (see
    module docstring and stage14_metric_baseline_contract.md Section 5)."""
    model_rate = model_metrics.get("High_Cost_Underprediction_Rate")
    b4_rate = b4_metrics.get("High_Cost_Underprediction_Rate")
    monitor: dict[str, Any] = {
        "model_rate_pct": model_rate,
        "b4_rate_pct": b4_rate,
        "2014_reference_pct": ACCEPTANCE_REFERENCE_HIGH_COST_UNDERPREDICTION_PCT,
        "flagged_vs_2014_reference": None,
        "better_than_b4_same_period": None,
    }
    if model_rate is not None:
        monitor["flagged_vs_2014_reference"] = model_rate > ACCEPTANCE_REFERENCE_HIGH_COST_UNDERPREDICTION_PCT + ACCEPTANCE_HIGH_COST_MONITOR_TOLERANCE_PP
    if model_rate is not None and b4_rate is not None:
        monitor["better_than_b4_same_period"] = model_rate < b4_rate
    return monitor


def classify_acceptance(model_metrics: dict[str, Any], b4_metrics: dict[str, Any], bundle_integrity_verified: bool) -> dict[str, Any]:
    """Returns {"classification": "ACCEPTED"|"CONDITIONAL"|"FAILED",
    "reasons": [...], "high_cost_risk_monitor": {...}}.

    This is an ENGINEERING classification, not a business SLA or a
    production-deployment decision -- it only says whether the frozen
    model meets predefined, provisional technical thresholds against the
    development-fit B4 baseline on the Protected Test.
    """
    reasons: list[str] = []
    high_cost_risk_monitor = _high_cost_risk_monitor(model_metrics, b4_metrics)

    if not bundle_integrity_verified:
        return {"classification": "FAILED", "reasons": ["model bundle integrity could not be verified -- evaluation result is not trustworthy"], "high_cost_risk_monitor": high_cost_risk_monitor}

    improvement_vs_b4 = (b4_metrics["MAE"] - model_metrics["MAE"]) / b4_metrics["MAE"]
    beats_b4_threshold = improvement_vs_b4 >= ACCEPTANCE_MIN_IMPROVEMENT_VS_B4
    reasons.append(f"MAE improvement vs B4: {improvement_vs_b4:.1%} (threshold: {ACCEPTANCE_MIN_IMPROVEMENT_VS_B4:.0%})")

    if improvement_vs_b4 <= 0:
        return {
            "classification": "FAILED",
            "reasons": reasons + ["model MAE is not better than B4 -- the frozen model does not beat the business baseline on the Protected Test"],
            "high_cost_risk_monitor": high_cost_risk_monitor,
        }

    validity_rate = model_metrics["Prediction_Validity_Rate"]
    meets_validity = validity_rate >= ACCEPTANCE_MIN_VALIDITY_RATE_PCT
    reasons.append(f"Prediction_Validity_Rate: {validity_rate:.2f}% (threshold: {ACCEPTANCE_MIN_VALIDITY_RATE_PCT}%)")

    # GATING high-cost criterion (D-173): same-period, relative to B4 --
    # not an absolute comparison against a near-ceiling 2014 reference.
    model_high_cost_rate = model_metrics.get("High_Cost_Underprediction_Rate")
    b4_high_cost_rate = b4_metrics.get("High_Cost_Underprediction_Rate")
    if model_high_cost_rate is None or b4_high_cost_rate is None:
        high_cost_ok = True  # no high-cost shipments in the eligible set -- nothing to gate on
        reasons.append("High-cost segment empty on this Protected Test run -- high-cost gate not applicable")
    else:
        high_cost_ok = model_high_cost_rate < b4_high_cost_rate
        reasons.append(f"High_Cost_Underprediction_Rate vs B4 (same period): model={model_high_cost_rate:.2f}% vs B4={b4_high_cost_rate:.2f}% ({'better' if high_cost_ok else 'not better'})")

    if beats_b4_threshold and meets_validity and high_cost_ok:
        classification = "ACCEPTED"
    else:
        classification = "CONDITIONAL"

    return {"classification": classification, "reasons": reasons, "high_cost_risk_monitor": high_cost_risk_monitor}
