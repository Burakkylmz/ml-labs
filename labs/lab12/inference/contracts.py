"""Shared exceptions and data contracts for the Stage 13 inference package."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ArtifactIntegrityError(Exception):
    """Raised when a model bundle fails checksum, manifest, or identity verification."""


class ModelCompatibilityError(Exception):
    """Raised when the runtime environment is incompatible with the bundle's recorded dependencies."""


class FeatureSchemaError(Exception):
    """Raised when an inference input violates the frozen feature schema."""


class PredictionValidationError(Exception):
    """Raised when a model produces a non-finite, negative, or otherwise invalid prediction."""


# Risk flag vocabulary -- frozen from the Stage 12 handoff contract (stage12_stage13_handoff.json).
RISK_FLAG_UNKNOWN_CATEGORY = "UNKNOWN_CATEGORY"
RISK_FLAG_MISSING_OPTIONAL_FEATURE = "MISSING_OPTIONAL_FEATURE"
RISK_FLAG_PREDICTION_OUTSIDE_REFERENCE_RANGE = "PREDICTION_OUTSIDE_REFERENCE_RANGE"
RISK_FLAG_INVALID_PREDICTION_DOMAIN = "INVALID_PREDICTION_DOMAIN"
RISK_FLAG_UNVERIFIED_FEATURE_AVAILABILITY = "UNVERIFIED_FEATURE_AVAILABILITY"
RISK_FLAG_INTERVAL_NOT_APPROVED = "INTERVAL_NOT_APPROVED"
RISK_FLAG_EXPLANATION_UNAVAILABLE = "EXPLANATION_UNAVAILABLE"

ALL_RISK_FLAGS = (
    RISK_FLAG_UNKNOWN_CATEGORY,
    RISK_FLAG_MISSING_OPTIONAL_FEATURE,
    RISK_FLAG_PREDICTION_OUTSIDE_REFERENCE_RANGE,
    RISK_FLAG_INVALID_PREDICTION_DOMAIN,
    RISK_FLAG_UNVERIFIED_FEATURE_AVAILABILITY,
    RISK_FLAG_INTERVAL_NOT_APPROVED,
    RISK_FLAG_EXPLANATION_UNAVAILABLE,
)


@dataclass(frozen=True)
class FeatureSchema:
    """The frozen Stage 07 Minimal Core feature contract, as recovered from real artifacts."""

    numeric: tuple[str, ...]
    categorical: tuple[str, ...]
    schema_version: str

    @property
    def all_features(self) -> tuple[str, ...]:
        return self.numeric + self.categorical

    @property
    def required_fields(self) -> tuple[str, ...]:
        # Every Minimal Core feature is required for a valid prediction -- none are
        # optional at the input-contract level (missing *values* are imputable,
        # but a missing *field* is a schema violation, per the Stage 13 design rule
        # that field presence and value missingness are evaluated separately).
        return self.all_features


@dataclass
class PredictionResult:
    """Output contract for a single prediction."""

    model_id: str
    trial_id: str
    model_version: str
    prediction_usd: float | None
    prediction_validity: str  # "valid" | "invalid"
    uncertainty_status: str = "disabled"
    explanation_status: str = "not_requested"
    explanation: dict[str, Any] | None = None
    risk_flags: list[str] = field(default_factory=list)
    invalid_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "trial_id": self.trial_id,
            "model_version": self.model_version,
            "prediction_usd": self.prediction_usd,
            "prediction_validity": self.prediction_validity,
            "uncertainty_status": self.uncertainty_status,
            "explanation_status": self.explanation_status,
            "explanation": self.explanation,
            "risk_flags": list(self.risk_flags),
            "invalid_reason": self.invalid_reason,
        }
