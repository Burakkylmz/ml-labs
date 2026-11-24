"""HTTP-layer request/response models.

Request bodies are typed as plain `dict`/`list[dict]` (not a fixed-field
Pydantic model) deliberately: the Stage 13 `FeatureSchemaValidator` is the
single source of truth for field presence, type, and value validation
(D-146). A second, parallel Pydantic schema here would risk drifting from
that contract and would duplicate validation logic the package already
owns. `PredictionResponse` exists only to document the output shape for
OpenAPI/Swagger -- the actual response body is always
`PredictionResult.to_dict()`.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class PredictionResponse(BaseModel):
    model_id: str
    trial_id: str
    model_version: str
    prediction_usd: float | None
    prediction_validity: str
    uncertainty_status: str
    explanation_status: str
    explanation: dict[str, Any] | None
    risk_flags: list[str]
    invalid_reason: str | None


class ErrorResponse(BaseModel):
    error_code: str
    detail: str


class HealthResponse(BaseModel):
    status: str


class ReadinessResponse(BaseModel):
    status: str
    model_id: str | None = None
    trial_id: str | None = None
    artifact_version: str | None = None
    reason: str | None = None
