"""Frozen constants and exceptions for the Stage 14 Phase B evaluation.

Every value here was recovered from an ALREADY-PUBLISHED Stage 05/08/11/13
artifact or doc -- none of it was derived by reading 2015 data during this
preparation task (see stage14_final_evaluation_protocol.md Section 1 for
provenance of each constant).
"""

from __future__ import annotations

from dataclasses import dataclass


class EvaluationError(Exception):
    """Base class for all Stage 14 Phase B evaluation errors."""


class GateError(EvaluationError):
    """Raised by PreUnlockGate when any pre-unlock check fails. Fail-closed:
    the Protected Test is never read if this is raised."""


class AlreadyEvaluatedError(EvaluationError):
    """Raised when a completed evaluation report already exists and no
    explicit override was given -- prevents a silent, accidental rerun."""


class FreezeIntegrityError(EvaluationError):
    """Raised when a freeze manifest fails to verify against its own
    recorded fingerprints (code, protocol, model, or dataset changed)."""


class DevelopmentPopulationIntegrityError(EvaluationError):
    """Raised when the loaded development population's B1 (Global Mean)
    does not match the frozen Stage 11 reference value -- added in the
    Pre-Unlock Audit (D-174) after discovering that this exact value is
    independently available (stage11_development_refit_report.json) and
    MUST be reproduced exactly if the development population is loaded
    correctly, since it is the same frozen 2006-2013 population Stage 11
    already fit B1 on."""


# -- Frozen model identity (Stage 13, unchanged) -----------------------------
EXPECTED_MODEL_ID = "M04"
EXPECTED_TRIAL_ID = "M04-T003"
EXPECTED_ARTIFACT_VERSION = "v1"
EXPECTED_MODEL_ARTIFACT_SHA256 = "71a451344f8b88a8d440d90325b88668cd3a8c16379425f5a4e95061bed77782"

# -- Frozen dataset / protocol fingerprints (Stage 05, unchanged) -----------
EXPECTED_DATASET_SHA256 = "9cffdb4ab8c6135b0f999c91b3a5c6e88a3c3dfc28c7c85feb9e97f986e3578a"
EXPECTED_STAGE05_PROTOCOL_FINGERPRINT = "b87ca0fde5fd9ddef45f191a0bb1c3e4e2a014b9c9641be5e8d20bb2458935e7"

# -- Frozen high-cost threshold ----------------------------------------------
# P90 of the FULL ELIGIBLE DEVELOPMENT (2006-2013, n=4987) population's
# Freight Cost -- frozen in Stage 11 BEFORE 2014 was read, reused unchanged
# for 2014 (stage11_external_validation_results.md Section 5) and, by the
# same frozen-before-the-period-is-read policy, reused unchanged for 2015.
# This is NOT recomputed from 2014 or 2015 data at any point.
HIGH_COST_THRESHOLD_USD = 23897.32

# -- Frozen development-population B1 reference (Pre-Unlock Audit finding) --
# The full 2006-2013 eligible development population (n=4987) is the SAME
# population Stage 11 already fit B1 on, for 2014 external validation
# (stage11_development_refit_report.json). Its Global Mean is therefore a
# known, frozen, independently-published number -- if Phase B's own
# development-population loader reconstructs the same population, it MUST
# reproduce this exact value. Used as a fail-closed integrity check in
# `runner.py` (D-174), not for fitting anything.
EXPECTED_B1_DEVELOPMENT_MEAN_USD = 10456.218411870865

# -- Baseline identifiers (Stage 08 registry) --------------------------------
BASELINE_B1_NAME = "Global Mean"
BASELINE_B4_NAME = "Hierarchical Segment Median"
BASELINE_MIN_SUPPORT = 10
BASELINE_SEGMENT_FEATURES = ("Shipment_Mode", "INCO_Term")

REASON_COMBINED_SEGMENT = "COMBINED_SEGMENT"
REASON_MODE_MEDIAN = "MODE_MEDIAN"
REASON_INCOTERM_MEDIAN = "INCOTERM_MEDIAN"
REASON_GLOBAL_MEDIAN = "GLOBAL_MEDIAN"

# -- Evaluation population policy (Stage 05 Section 2, Stage 11 Section 6) --
DEVELOPMENT_SPLIT_LABEL = "Train"
PROTECTED_SPLIT_LABEL = "Protected_Test"
GROUPING_KEY = "Shipment_Key"
TARGET_COLUMN_RAW = "Freight Cost (USD)"

REQUIRED_SCHEMA_FIELDS = (
    "Line_Item_Qty_Sum", "Line_Item_Value_Sum",
    "Shipment_Mode", "INCO_Term", "Country", "Product_Group",
)


@dataclass(frozen=True)
class MetricSpec:
    """One frozen metric definition: name, unit, and a one-line formula note
    for the protocol doc. See `metrics.py` for the actual implementation."""

    name: str
    unit: str
    formula: str


# -- Technical acceptance rules (ENGINEERING thresholds, NOT a business- --
# -- approved SLA -- see stage14_metric_baseline_contract.md Section 5). --
# Provisional, engineer-set thresholds, frozen before any 2015 access:
ACCEPTANCE_MIN_IMPROVEMENT_VS_B4 = 0.10  # primary model MAE must beat B4 MAE by >= 10%
ACCEPTANCE_MIN_VALIDITY_RATE_PCT = 99.0  # Prediction_Validity_Rate must be >= this

# -- High-cost risk: GATING criterion revised in the Pre-Unlock Audit (D-173) --
# The ORIGINAL rule ("2015 rate <= 2014 reference (89.93%) + 10pp = 99.93%")
# is, on inspection, nearly vacuous: the metric is bounded at 100%, the 2014
# reference is already near that ceiling, and BOTH baselines (B1, B4) already
# score exactly 100% on 2014 -- so a fixed +10pp-over-an-near-ceiling-reference
# tolerance would only ever fail a model that underpredicts literally every
# single high-cost shipment, which provides essentially no discriminating
# power. See stage14_metric_baseline_contract.md Section 5 (v2) for the full
# analysis. It is RECLASSIFIED below as a monitored risk indicator (always
# reported, never gates the classification) and REPLACED, as the actual
# gating criterion, by a same-period, relative comparison against B4 (no
# arbitrary tolerance constant needed: the model must simply underpredict
# high-cost shipments LESS often than B4 does on the SAME eligible segment).
ACCEPTANCE_REFERENCE_HIGH_COST_UNDERPREDICTION_PCT = 89.93  # Stage 11's 2014 result -- MONITORING reference only, not a gate
ACCEPTANCE_HIGH_COST_MONITOR_TOLERANCE_PP = 10.0  # retained for the monitor's "flag" threshold, not for gating

PRIMARY_METRIC = MetricSpec("MAE", "USD", "mean(|actual - prediction|) over eligible shipments")

SECONDARY_METRICS = (
    MetricSpec("RMSE", "USD", "sqrt(mean((actual - prediction)^2))"),
    MetricSpec("Median_AE", "USD", "median(|actual - prediction|)"),
    MetricSpec("WAPE", "%", "100 * sum(|actual - prediction|) / sum(|actual|)"),
    MetricSpec("Bias", "USD", "mean(prediction - actual); negative = systematic underprediction"),
    MetricSpec("P90_AE", "USD", "90th percentile of |actual - prediction|"),
    MetricSpec("P95_AE", "USD", "95th percentile of |actual - prediction|"),
    MetricSpec("Prediction_Validity_Rate", "%", "100 * valid predictions / total eligible shipments"),
    MetricSpec("Negative_Prediction_Count", "count", "count of raw predictions < 0 before invalid-reporting"),
    MetricSpec("High_Cost_MAE", "USD", f"MAE restricted to actual >= {HIGH_COST_THRESHOLD_USD} USD"),
    MetricSpec("High_Cost_Underprediction_Rate", "%", "100 * (prediction < actual) / n in the high-cost segment"),
)
