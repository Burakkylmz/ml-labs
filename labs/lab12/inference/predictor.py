"""FreightCostPredictor -- the Stage 13 reusable inference interface.

Loads a trusted, versioned model bundle once and serves single/batch
predictions without ever refitting the model. This is the only class
Stage 14's future API layer is expected to depend on.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .artifact_store import compute_sha256
from .contracts import FeatureSchema, FeatureSchemaError, PredictionResult, PredictionValidationError
from .explainability import ShapExplainer
from .model_loader import TrustedBundleLoader
from .contracts import RISK_FLAG_EXPLANATION_UNAVAILABLE
from .risk_flags import evaluate_prediction_flags, interval_requested_flag, structural_flags
from .schemas import FeatureSchemaValidator


def _extract_fitted_categories(fitted_pipeline: Any, categorical_features: tuple[str, ...]) -> dict[str, set[str]]:
    preprocessor = fitted_pipeline.named_steps["preprocessor"]
    encoder = preprocessor.named_transformers_["categorical"].named_steps["encoder"]
    return {feat: set(cats.tolist()) for feat, cats in zip(categorical_features, encoder.categories_)}


class FreightCostPredictor:
    def __init__(self, fitted_pipeline: Any, manifest: dict[str, Any], max_batch_size: int = 100, max_batch_explanations: int = 10):
        self.fitted_pipeline = fitted_pipeline
        self.manifest = manifest
        self.max_batch_size = max_batch_size
        self.max_batch_explanations = max_batch_explanations

        schema_dict = manifest["feature_schema_inline"]
        self.schema = FeatureSchema(
            numeric=tuple(schema_dict["numeric"]),
            categorical=tuple(schema_dict["categorical"]),
            schema_version=manifest["feature_schema_version"],
        )
        fitted_categories = _extract_fitted_categories(fitted_pipeline, self.schema.categorical)
        self.validator = FeatureSchemaValidator(self.schema, fitted_categories, strict=True)

        self.reference_min_usd = float(manifest["reference_stats"]["min_usd"])
        self.reference_max_usd = float(manifest["reference_stats"]["max_usd"])

        preprocessor = fitted_pipeline.named_steps["preprocessor"]
        self._encoded_feature_names = list(preprocessor.get_feature_names_out())
        self._raw_source_map = self._build_raw_source_map()
        self._explainer: ShapExplainer | None = None  # built lazily on first explain=True call

    def _build_raw_source_map(self) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for enc_name in self._encoded_feature_names:
            if enc_name.startswith("numeric__"):
                mapping[enc_name] = enc_name.replace("numeric__", "")
            else:
                mapping[enc_name] = enc_name.replace("categorical__", "").rsplit("_", 1)[0]
        return mapping

    @classmethod
    def load(cls, bundle_dir: Path, allowed_root: Path, expected_model_id: str, expected_trial_id: str, max_batch_size: int = 100, max_batch_explanations: int = 10) -> "FreightCostPredictor":
        loader = TrustedBundleLoader(allowed_root=allowed_root, expected_model_id=expected_model_id, expected_trial_id=expected_trial_id)
        fitted_pipeline, manifest = loader.load(bundle_dir)
        return cls(fitted_pipeline, manifest, max_batch_size=max_batch_size, max_batch_explanations=max_batch_explanations)

    def _get_explainer(self) -> ShapExplainer:
        if self._explainer is None:
            fitted_estimator = self.fitted_pipeline.named_steps["model"]
            self._explainer = ShapExplainer(fitted_estimator, self._encoded_feature_names, self._raw_source_map)
        return self._explainer

    def _predict_raw(self, cleaned_records: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
        df = pd.DataFrame(cleaned_records, columns=list(self.schema.all_features))
        preprocessor = self.fitted_pipeline.named_steps["preprocessor"]
        encoded = preprocessor.transform(df)
        predictions = self.fitted_pipeline.named_steps["model"].predict(encoded)
        return predictions, encoded

    def predict_one(self, shipment: dict[str, Any], explain: bool = False, request_interval: bool = False) -> PredictionResult:
        return self.predict_batch([shipment], explain=explain, request_interval=request_interval)[0]

    def predict_batch(self, shipments: list[dict[str, Any]], explain: bool = False, request_interval: bool = False) -> list[PredictionResult]:
        if len(shipments) == 0:
            return []
        if len(shipments) > self.max_batch_size:
            raise FeatureSchemaError(f"BATCH_SIZE_EXCEEDED: {len(shipments)} > max_batch_size={self.max_batch_size}")
        if explain and len(shipments) > self.max_batch_explanations:
            raise FeatureSchemaError(f"EXPLANATION_BATCH_LIMIT_EXCEEDED: {len(shipments)} > max_batch_explanations={self.max_batch_explanations} -- call with explain=False or a smaller batch")

        # Atomic batch validation: any single schema error rejects the whole batch (Stage 13 prototype policy).
        cleaned_records = [self.validator.validate(s) for s in shipments]
        cleaned = [c for c, _flags in cleaned_records]
        per_row_schema_flags = [flags for _c, flags in cleaned_records]

        predictions, encoded = self._predict_raw(cleaned)

        results: list[PredictionResult] = []
        for i, pred in enumerate(predictions):
            risk_flags = list(per_row_schema_flags[i]) + structural_flags() + interval_requested_flag(request_interval)
            pred_value = float(pred)

            if not math.isfinite(pred_value):
                raise PredictionValidationError(f"Model produced a non-finite prediction: {pred_value}")
            if pred_value < 0:
                results.append(PredictionResult(
                    model_id=self.manifest["model_id"], trial_id=self.manifest["trial_id"], model_version=self.manifest["artifact_version"],
                    prediction_usd=None, prediction_validity="invalid", invalid_reason=f"negative prediction ({pred_value:.2f} USD) -- not clipped, reported as invalid",
                    risk_flags=sorted(set(risk_flags)),
                ))
                continue

            risk_flags += evaluate_prediction_flags(pred_value, self.reference_min_usd, self.reference_max_usd)

            explanation = None
            explanation_status = "not_requested"
            if explain:
                try:
                    explanation = self._get_explainer().explain_one(encoded[i], pred_value)
                    explanation_status = "available"
                except Exception as exc:  # noqa: BLE001 -- deliberately broad: any explainer failure degrades to a reported, non-fabricated status
                    explanation_status = "failed"
                    explanation = {"explanation_status": "failed", "reason": str(exc)}
                    risk_flags.append(RISK_FLAG_EXPLANATION_UNAVAILABLE)

            results.append(PredictionResult(
                model_id=self.manifest["model_id"], trial_id=self.manifest["trial_id"], model_version=self.manifest["artifact_version"],
                prediction_usd=pred_value, prediction_validity="valid",
                explanation_status=explanation_status, explanation=explanation,
                risk_flags=sorted(set(risk_flags)),
            ))
        return results
