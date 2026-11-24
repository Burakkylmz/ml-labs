"""FinalEvaluationRunner -- the actual Phase B logic. Reachable ONLY with a
valid `gate.UnlockToken`; `population.load_protected_population` enforces
this structurally, so there is no path from a normal pytest collection or
notebook cell to this module's protected-data branch.

Reuses `inference.predictor.FreightCostPredictor` as the single source of
truth for predictions (master prompt Section 2/3: no reimplementation, no
retraining, no changed preprocessing/features/prediction behavior). The
one exception is reading `FreightCostPredictor._predict_raw()` directly
for `Negative_Prediction_Count` -- the public `PredictionResult` contract
deliberately hides the raw negative value behind `invalid_reason` text
(Stage 13, D-149), so recovering it requires the same internal method
`predict_batch()` itself already calls; nothing is reimplemented or
behaviorally changed, and `inference/` is not modified.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .acceptance import classify_acceptance
from .baselines import GlobalMeanBaseline, HierarchicalMedianBaseline
from .contracts import DevelopmentPopulationIntegrityError, EXPECTED_MODEL_ID, EXPECTED_TRIAL_ID, REQUIRED_SCHEMA_FIELDS
from .gate import UnlockToken
from .metrics import compute_all_metrics
from .population import load_development_population, load_protected_population


def _shipment_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return df[list(REQUIRED_SCHEMA_FIELDS)].to_dict(orient="records")


def _predict_with_raw(predictor: Any, records: list[dict[str, Any]], batch_size: int) -> tuple[list[dict[str, Any]], np.ndarray]:
    """Returns (list of PredictionResult.to_dict(), raw unmasked predictions array)."""
    all_results: list[dict[str, Any]] = []
    all_raw: list[float] = []
    for start in range(0, len(records), batch_size):
        chunk = records[start:start + batch_size]
        results = predictor.predict_batch(chunk)
        all_results.extend(r.to_dict() for r in results)
        cleaned = [predictor.validator.validate(s)[0] for s in chunk]
        raw_predictions, _encoded = predictor._predict_raw(cleaned)
        all_raw.extend(float(v) for v in raw_predictions)
    return all_results, np.array(all_raw, dtype=float)


class FinalEvaluationRunner:
    def __init__(
        self, *, dataset_path: Path, split_manifest_path: Path, model_bundle_dir: Path, allowed_root: Path, report_path: Path,
        expected_development_b1_mean_usd: float | None = None, development_mean_tolerance_usd: float = 1e-6,
    ):
        self.dataset_path = dataset_path
        self.split_manifest_path = split_manifest_path
        self.model_bundle_dir = model_bundle_dir
        self.allowed_root = allowed_root
        self.report_path = report_path
        # Pre-Unlock Audit (D-174): when set, the freshly-fit B1 mean must
        # reproduce this frozen Stage 11 reference EXACTLY (same population),
        # checked BEFORE the Protected Test is ever read. `None` (the
        # default) skips the check -- used by synthetic/test fixtures whose
        # fabricated population has no reason to match the real mean.
        self.expected_development_b1_mean_usd = expected_development_b1_mean_usd
        self.development_mean_tolerance_usd = development_mean_tolerance_usd

    def run(self, unlock_token: UnlockToken) -> dict[str, Any]:
        if not isinstance(unlock_token, UnlockToken) or not unlock_token.is_valid():
            raise PermissionError("FinalEvaluationRunner.run() requires a valid, unconsumed UnlockToken")

        from inference.predictor import FreightCostPredictor

        predictor = FreightCostPredictor.load(
            bundle_dir=self.model_bundle_dir, allowed_root=self.allowed_root,
            expected_model_id=EXPECTED_MODEL_ID, expected_trial_id=EXPECTED_TRIAL_ID,
        )
        bundle_integrity_verified = True  # FreightCostPredictor.load() raised already if not

        development_population = load_development_population(self.dataset_path, self.split_manifest_path)
        b1 = GlobalMeanBaseline().fit(development_population["Target"])
        b4 = HierarchicalMedianBaseline().fit(development_population)

        if self.expected_development_b1_mean_usd is not None:
            drift = abs(b1.mean_ - self.expected_development_b1_mean_usd)
            if drift > self.development_mean_tolerance_usd:
                raise DevelopmentPopulationIntegrityError(
                    f"Development population B1 mean ({b1.mean_}) does not match the frozen Stage 11 "
                    f"reference ({self.expected_development_b1_mean_usd}), drift={drift} USD -- refusing to "
                    "proceed to the Protected Test with a possibly-incorrect development population."
                )

        protected_population = load_protected_population(self.dataset_path, self.split_manifest_path, unlock_token=unlock_token)
        unlock_token.consume()  # one-time use: this is the only read of 2015 data in the entire run

        records = _shipment_records(protected_population)
        model_results, raw_predictions = _predict_with_raw(predictor, records, predictor.max_batch_size)

        actual = protected_population["Target"].to_numpy()
        validity_flags = [r["prediction_validity"] for r in model_results]
        valid_mask = np.array([flag == "valid" for flag in validity_flags])
        model_prediction = np.array([r["prediction_usd"] if r["prediction_usd"] is not None else np.nan for r in model_results])

        model_metrics = compute_all_metrics(actual[valid_mask], model_prediction[valid_mask], validity_flags, raw_predictions)

        b4_prediction, b4_reasons = b4.predict(protected_population)
        b4_metrics = compute_all_metrics(actual, b4_prediction, ["valid"] * len(actual), b4_prediction)

        b1_prediction = b1.predict(len(protected_population))
        b1_metrics = compute_all_metrics(actual, b1_prediction, ["valid"] * len(actual), b1_prediction)

        acceptance = classify_acceptance(model_metrics, b4_metrics, bundle_integrity_verified)

        report = {
            "evaluated_at_unix": time.time(),
            "n_protected_eligible": len(protected_population),
            "model": {"model_id": EXPECTED_MODEL_ID, "trial_id": EXPECTED_TRIAL_ID, "metrics": model_metrics},
            "b1_global_mean": {"metrics": b1_metrics},
            "b4_hierarchical_median": {"metrics": b4_metrics, "fallback_reason_counts": pd.Series(b4_reasons).value_counts().to_dict()},
            "acceptance": acceptance,
        }
        self.report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report
