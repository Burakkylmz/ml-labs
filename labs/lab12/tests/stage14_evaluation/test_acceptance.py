import pytest

from evaluation.acceptance import classify_acceptance


def _metrics(mae, validity=100.0, high_cost_rate=85.0):
    return {"MAE": mae, "Prediction_Validity_Rate": validity, "High_Cost_Underprediction_Rate": high_cost_rate}


def test_accepted_when_model_clearly_beats_b4_with_good_validity_and_lower_high_cost_rate():
    result = classify_acceptance(_metrics(6000.0, high_cost_rate=80.0), _metrics(9000.0, high_cost_rate=100.0), bundle_integrity_verified=True)
    assert result["classification"] == "ACCEPTED"


def test_failed_when_integrity_not_verified_regardless_of_metrics():
    result = classify_acceptance(_metrics(100.0), _metrics(9000.0), bundle_integrity_verified=False)
    assert result["classification"] == "FAILED"


def test_failed_when_model_does_not_beat_b4():
    result = classify_acceptance(_metrics(9500.0), _metrics(9000.0), bundle_integrity_verified=True)
    assert result["classification"] == "FAILED"


def test_conditional_when_improvement_below_threshold():
    """Beats B4 by only ~5% (< the 10% acceptance threshold) -> CONDITIONAL, not ACCEPTED."""
    result = classify_acceptance(_metrics(8550.0, high_cost_rate=80.0), _metrics(9000.0, high_cost_rate=100.0), bundle_integrity_verified=True)
    assert result["classification"] == "CONDITIONAL"


def test_conditional_when_validity_rate_below_threshold():
    result = classify_acceptance(_metrics(6000.0, validity=97.0, high_cost_rate=80.0), _metrics(9000.0, high_cost_rate=100.0), bundle_integrity_verified=True)
    assert result["classification"] == "CONDITIONAL"


def test_classification_never_claims_business_sla():
    """Acceptance is an engineering classification only -- no 'business_approved'
    or 'sla' field should ever appear in the result."""
    result = classify_acceptance(_metrics(6000.0), _metrics(9000.0), bundle_integrity_verified=True)
    assert "business_approved" not in result
    assert "sla" not in {k.lower() for k in result}


# -- D-173: the revised, relative-to-B4 high-cost gate ----------------------

def test_conditional_when_model_high_cost_rate_not_better_than_b4_same_period():
    """Model matches B4's high-cost underprediction rate exactly (not strictly
    better) -> the gate must trip, even though both are far below the old
    99.93% absolute ceiling."""
    result = classify_acceptance(_metrics(6000.0, high_cost_rate=90.0), _metrics(9000.0, high_cost_rate=90.0), bundle_integrity_verified=True)
    assert result["classification"] == "CONDITIONAL"


def test_accepted_even_when_model_matches_the_old_2014_reference_rate_if_still_better_than_b4():
    """The OLD rule would have evaluated 89.93% against a fixed 99.93% ceiling
    (trivially passing). The NEW rule correctly still gates on whether the
    model beats B4 in the SAME run, which is the statistically meaningful
    comparison -- this is the concrete case the Pre-Unlock Audit flagged."""
    result = classify_acceptance(_metrics(6000.0, high_cost_rate=89.93), _metrics(9000.0, high_cost_rate=95.0), bundle_integrity_verified=True)
    assert result["classification"] == "ACCEPTED"


def test_high_cost_risk_monitor_is_informational_and_never_gates():
    """Even when the OLD 2014-reference monitor would flag (model rate far
    above 99.93%), the field is reported but does not change the
    classification by itself -- only the relative-to-B4 comparison gates."""
    result = classify_acceptance(_metrics(6000.0, high_cost_rate=99.99), _metrics(9000.0, high_cost_rate=100.0), bundle_integrity_verified=True)
    assert result["high_cost_risk_monitor"]["flagged_vs_2014_reference"] is True
    assert result["high_cost_risk_monitor"]["better_than_b4_same_period"] is True
    assert result["classification"] == "ACCEPTED"  # still beats B4 in the same period, despite the flag


def test_high_cost_gate_not_applicable_when_segment_empty():
    result = classify_acceptance(
        {"MAE": 6000.0, "Prediction_Validity_Rate": 100.0, "High_Cost_Underprediction_Rate": None},
        {"MAE": 9000.0, "Prediction_Validity_Rate": 100.0, "High_Cost_Underprediction_Rate": None},
        bundle_integrity_verified=True,
    )
    assert result["classification"] == "ACCEPTED"
    assert result["high_cost_risk_monitor"]["better_than_b4_same_period"] is None
