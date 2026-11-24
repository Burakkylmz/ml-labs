"""Exception -> HTTP status mapping (stage14_api_deployment_contract.md Section 11).

| Exception                 | HTTP Status |
|----------------------------|-------------|
| FeatureSchemaError         | 422         |
| PredictionValidationError  | 500         |
| ArtifactIntegrityError     | 503         |
| ModelCompatibilityError    | 503         |

The inference package raises these with a message of the form
"ERROR_CODE: human detail" (see inference/schemas.py, inference/contracts.py).
The leading token is surfaced as a stable `error_code` field so API
consumers can branch on it without parsing free text.
"""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from inference.contracts import (
    ArtifactIntegrityError,
    FeatureSchemaError,
    ModelCompatibilityError,
    PredictionValidationError,
)

_KNOWN_CODES = (
    "MISSING_REQUIRED_FIELD",
    "UNKNOWN_FIELD",
    "INVALID_FIELD_TYPE",
    "INVALID_NUMERIC_VALUE",
    "INVALID_SHIPMENT_STRUCTURE",
    "BATCH_SIZE_EXCEEDED",
    "EXPLANATION_BATCH_LIMIT_EXCEEDED",
)


def _extract_error_code(message: str) -> str:
    head = message.split(":", 1)[0].strip()
    return head if head in _KNOWN_CODES else "VALIDATION_ERROR"


def _error_body(error_code: str, detail: str) -> dict[str, str]:
    return {"error_code": error_code, "detail": detail}


async def feature_schema_error_handler(request: Request, exc: FeatureSchemaError) -> JSONResponse:
    message = str(exc)
    return JSONResponse(status_code=422, content=_error_body(_extract_error_code(message), message))


async def prediction_validation_error_handler(request: Request, exc: PredictionValidationError) -> JSONResponse:
    return JSONResponse(status_code=500, content=_error_body("PREDICTION_VALIDATION_ERROR", str(exc)))


async def artifact_integrity_error_handler(request: Request, exc: ArtifactIntegrityError) -> JSONResponse:
    return JSONResponse(status_code=503, content=_error_body("ARTIFACT_INTEGRITY_ERROR", str(exc)))


async def model_compatibility_error_handler(request: Request, exc: ModelCompatibilityError) -> JSONResponse:
    return JSONResponse(status_code=503, content=_error_body("MODEL_COMPATIBILITY_ERROR", str(exc)))


EXCEPTION_HANDLERS = {
    FeatureSchemaError: feature_schema_error_handler,
    PredictionValidationError: prediction_validation_error_handler,
    ArtifactIntegrityError: artifact_integrity_error_handler,
    ModelCompatibilityError: model_compatibility_error_handler,
}
