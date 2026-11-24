"""Optional, bounded SHAP explanation for a single prediction.

Reuses the Stage 12-accepted default policy: `shap.TreeExplainer` with the
`tree_path_dependent` perturbation assumption (no explicit background
dataset), `model_output="raw"`. Stage 12 found that `tree_path_dependent`
and `interventional` produce materially different attributions for at
least one feature -- this module does not attempt to resolve that, it only
reports which assumption was used.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import shap


class ShapExplainer:
    def __init__(self, fitted_estimator: Any, encoded_feature_names: list[str], raw_source_map: dict[str, str], additivity_tolerance_usd: float = 1.0):
        self._explainer = shap.TreeExplainer(fitted_estimator, model_output="raw")
        self.encoded_feature_names = list(encoded_feature_names)
        self.raw_source_map = dict(raw_source_map)
        self.additivity_tolerance_usd = additivity_tolerance_usd
        self.background_policy = "tree_path_dependent"
        self.shap_version = shap.__version__

    def explain_one(self, encoded_row: np.ndarray, prediction_usd: float) -> dict[str, Any]:
        shap_values = self._explainer.shap_values(encoded_row.reshape(1, -1))[0]
        base_value = float(np.asarray(self._explainer.expected_value).reshape(-1)[0])

        additivity_diff = abs(prediction_usd - (base_value + float(shap_values.sum())))
        additivity_valid = additivity_diff <= self.additivity_tolerance_usd

        grouped: dict[str, float] = {}
        for enc_name, phi in zip(self.encoded_feature_names, shap_values):
            raw_name = self.raw_source_map.get(enc_name, enc_name)
            grouped[raw_name] = grouped.get(raw_name, 0.0) + float(phi)

        contributions = [
            {"feature": raw_name, "signed_contribution_usd": value, "absolute_contribution_usd": abs(value)}
            for raw_name, value in sorted(grouped.items(), key=lambda kv: -abs(kv[1]))
        ]

        return {
            "explanation_status": "available",
            "method": "tree_shap",
            "model_output": "raw",
            "background_policy": self.background_policy,
            "shap_library_version": self.shap_version,
            "base_value_usd": base_value,
            "feature_contributions": contributions,
            "additivity_valid": additivity_valid,
            "additivity_diff_usd": additivity_diff,
        }
