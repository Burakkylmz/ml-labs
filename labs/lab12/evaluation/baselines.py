"""B1 (Global Mean) and B4 (Hierarchical Segment Median) baselines.

Recovered from stage08_baseline_design.md Sections 6 and 10-12. Both are
fit ONLY on the development population (`population.load_development_population`)
-- never on 2014 or 2015 labels (stage08_baseline_design.md Section 14:
"segment medianlari/mean'leri yalnizca fold-training uzerinde fit edildi").
Here, "fold-training" becomes "the full development population" because
Phase B is a single, final fit on all permitted data (Stage 05 Section 13),
exactly mirroring how M04-T003 itself was refit in Stage 13.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .contracts import (
    BASELINE_MIN_SUPPORT,
    BASELINE_SEGMENT_FEATURES,
    REASON_COMBINED_SEGMENT,
    REASON_GLOBAL_MEDIAN,
    REASON_INCOTERM_MEDIAN,
    REASON_MODE_MEDIAN,
)


class GlobalMeanBaseline:
    """B1. No features; predicts the development population's target mean."""

    def fit(self, y: pd.Series) -> "GlobalMeanBaseline":
        if len(y) == 0:
            raise ValueError("Cannot fit GlobalMeanBaseline on an empty target series")
        self.mean_: float = float(y.mean())
        return self

    def predict(self, n: int) -> np.ndarray:
        return np.full(n, self.mean_, dtype=float)


class HierarchicalMedianBaseline:
    """B4. Fallback chain: combined (Shipment_Mode + INCO_Term) segment median
    (if support >= min_support) -> Shipment_Mode median (if support >=
    min_support) -> INCO_Term median (if support >= min_support) -> global
    median. Every level is fit on development-only data; `predict()` never
    receives or uses target values (Stage 08 leakage-prevention invariant)."""

    def __init__(self, min_support: int = BASELINE_MIN_SUPPORT):
        self.min_support = min_support
        self.mode_col, self.incoterm_col = BASELINE_SEGMENT_FEATURES

    def fit(self, df: pd.DataFrame) -> "HierarchicalMedianBaseline":
        if len(df) == 0:
            raise ValueError("Cannot fit HierarchicalMedianBaseline on an empty dataframe")
        required = {self.mode_col, self.incoterm_col, "Target"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"fit() dataframe is missing required columns: {missing}")

        self.global_median_: float = float(df["Target"].median())

        combined_counts = df.groupby([self.mode_col, self.incoterm_col]).size()
        combined_medians = df.groupby([self.mode_col, self.incoterm_col])["Target"].median()
        self.combined_medians_: dict[tuple[Any, Any], float] = {
            key: float(combined_medians[key]) for key in combined_counts[combined_counts >= self.min_support].index
        }

        mode_counts = df.groupby(self.mode_col).size()
        mode_medians = df.groupby(self.mode_col)["Target"].median()
        self.mode_medians_: dict[Any, float] = {
            key: float(mode_medians[key]) for key in mode_counts[mode_counts >= self.min_support].index
        }

        incoterm_counts = df.groupby(self.incoterm_col).size()
        incoterm_medians = df.groupby(self.incoterm_col)["Target"].median()
        self.incoterm_medians_: dict[Any, float] = {
            key: float(incoterm_medians[key]) for key in incoterm_counts[incoterm_counts >= self.min_support].index
        }
        return self

    def _predict_one(self, mode: Any, incoterm: Any) -> tuple[float, str]:
        if (mode, incoterm) in self.combined_medians_:
            return self.combined_medians_[(mode, incoterm)], REASON_COMBINED_SEGMENT
        if mode in self.mode_medians_:
            return self.mode_medians_[mode], REASON_MODE_MEDIAN
        if incoterm in self.incoterm_medians_:
            return self.incoterm_medians_[incoterm], REASON_INCOTERM_MEDIAN
        return self.global_median_, REASON_GLOBAL_MEDIAN

    def predict(self, df: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
        predictions: list[float] = []
        reasons: list[str] = []
        for mode, incoterm in zip(df[self.mode_col], df[self.incoterm_col]):
            value, reason = self._predict_one(mode, incoterm)
            predictions.append(value)
            reasons.append(reason)
        return np.array(predictions, dtype=float), reasons
