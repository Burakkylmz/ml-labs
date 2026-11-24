import numpy as np
import pandas as pd
import pytest

from evaluation.baselines import GlobalMeanBaseline, HierarchicalMedianBaseline
from evaluation.contracts import REASON_COMBINED_SEGMENT, REASON_GLOBAL_MEDIAN, REASON_MODE_MEDIAN


def test_global_mean_baseline_b1(development_frame):
    b1 = GlobalMeanBaseline().fit(development_frame["Target"])
    assert b1.mean_ == pytest.approx(development_frame["Target"].mean())
    preds = b1.predict(5)
    assert len(preds) == 5
    assert np.all(preds == b1.mean_)


def test_global_mean_baseline_empty_raises():
    with pytest.raises(ValueError):
        GlobalMeanBaseline().fit(pd.Series([], dtype=float))


def test_hierarchical_median_combined_segment_used_when_support_sufficient():
    df = pd.DataFrame({
        "Shipment_Mode": ["Air"] * 15 + ["Ocean"] * 15,
        "INCO_Term": ["EXW"] * 15 + ["DDP"] * 15,
        "Target": [1000.0] * 15 + [2000.0] * 15,
    })
    b4 = HierarchicalMedianBaseline(min_support=10).fit(df)
    preds, reasons = b4.predict(pd.DataFrame({"Shipment_Mode": ["Air"], "INCO_Term": ["EXW"]}))
    assert preds[0] == pytest.approx(1000.0)
    assert reasons[0] == REASON_COMBINED_SEGMENT


def test_hierarchical_median_falls_back_to_mode_when_combined_support_low():
    df = pd.DataFrame({
        "Shipment_Mode": ["Air"] * 12 + ["Air"] * 3,
        "INCO_Term": ["EXW"] * 12 + ["DDP"] * 3,  # Air+DDP support=3 (<10)
        "Target": [1000.0] * 12 + [5000.0] * 3,
    })
    b4 = HierarchicalMedianBaseline(min_support=10).fit(df)
    preds, reasons = b4.predict(pd.DataFrame({"Shipment_Mode": ["Air"], "INCO_Term": ["DDP"]}))
    assert reasons[0] == REASON_MODE_MEDIAN
    assert preds[0] == pytest.approx(1000.0)  # Air's own median (all 15 Air rows)


def test_hierarchical_median_falls_back_to_global_for_unseen_combination():
    df = pd.DataFrame({
        "Shipment_Mode": ["Air"] * 10,
        "INCO_Term": ["EXW"] * 10,
        "Target": [1000.0] * 10,
    })
    b4 = HierarchicalMedianBaseline(min_support=10).fit(df)
    preds, reasons = b4.predict(pd.DataFrame({"Shipment_Mode": ["Truck"], "INCO_Term": ["FCA"]}))
    assert reasons[0] == REASON_GLOBAL_MEDIAN
    assert preds[0] == pytest.approx(1000.0)


def test_hierarchical_median_empty_fit_raises():
    with pytest.raises(ValueError):
        HierarchicalMedianBaseline().fit(pd.DataFrame(columns=["Shipment_Mode", "INCO_Term", "Target"]))


def test_hierarchical_median_predict_signature_never_accepts_target():
    """No model-fitting/leakage during evaluation: predict() must only take
    feature columns -- it has no way to receive target values at predict time."""
    import inspect

    sig = inspect.signature(HierarchicalMedianBaseline.predict)
    assert "y" not in sig.parameters and "target" not in [p.lower() for p in sig.parameters]


def test_b1_and_b4_comparison_on_same_population(development_frame):
    b1 = GlobalMeanBaseline().fit(development_frame["Target"])
    b4 = HierarchicalMedianBaseline().fit(development_frame)

    b1_pred = b1.predict(len(development_frame))
    b4_pred, _reasons = b4.predict(development_frame)

    b1_mae = np.mean(np.abs(development_frame["Target"] - b1_pred))
    b4_mae = np.mean(np.abs(development_frame["Target"] - b4_pred))
    # Segment-aware B4 must be at least as informative as the no-feature B1
    # on this synthetic, strongly mode-separated population.
    assert b4_mae <= b1_mae
