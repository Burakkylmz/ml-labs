"""Stage 14 (Phase A) FastAPI service wrapping `FreightCostPredictor`.

Run (from repo root, inside the existing `ml-lab` container or locally):

    uv run uvicorn api.app:app --app-dir labs/lab12 --host 0.0.0.0 --port 8000

`labs/lab12` has no `__init__.py` (same convention as `labs/lab12/tests`),
so it is addressed via `--app-dir` rather than a dotted `labs.lab12...`
import path.

Scope: Phase A only (REST API, Docker reuse, automated testing). This
module never reads, parses, or references the 2015 Protected Test; Phase B
(final evaluation) is a separate, explicitly-gated activity.
"""

from __future__ import annotations

import logging
import math
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse

_LAB12_ROOT = Path(__file__).resolve().parents[1]
if str(_LAB12_ROOT) not in sys.path:
    sys.path.insert(0, str(_LAB12_ROOT))

from inference.contracts import PredictionResult  # noqa: E402
from inference.predictor import FreightCostPredictor  # noqa: E402

from .config import (  # noqa: E402
    BUNDLE_ROOT,
    BUNDLE_VERSION_DIR,
    CANARY_SHIPMENT,
    EXPECTED_MODEL_ID,
    EXPECTED_TRIAL_ID,
    MAX_BATCH_EXPLANATIONS,
    MAX_BATCH_SIZE,
)
from .errors import EXCEPTION_HANDLERS  # noqa: E402

logger = logging.getLogger("lab12.stage14.api")


def _log_result(endpoint: str, result: PredictionResult) -> None:
    logger.info(
        "endpoint=%s model_id=%s trial_id=%s artifact_version=%s prediction_validity=%s risk_flags=%s",
        endpoint, result.model_id, result.trial_id, result.model_version, result.prediction_validity, result.risk_flags,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.predictor = None
    app.state.ready = False
    app.state.startup_error = None
    try:
        predictor = FreightCostPredictor.load(
            bundle_dir=BUNDLE_VERSION_DIR, allowed_root=BUNDLE_ROOT,
            expected_model_id=EXPECTED_MODEL_ID, expected_trial_id=EXPECTED_TRIAL_ID,
            max_batch_size=MAX_BATCH_SIZE, max_batch_explanations=MAX_BATCH_EXPLANATIONS,
        )
        canary = predictor.predict_one(CANARY_SHIPMENT)
        if canary.prediction_validity != "valid" or canary.prediction_usd is None or not math.isfinite(canary.prediction_usd):
            raise RuntimeError(f"Canary prediction failed validity check: {canary.to_dict()}")
        app.state.predictor = predictor
        app.state.ready = True
        logger.info(
            "startup complete: model_id=%s trial_id=%s artifact_version=%s canary_prediction_usd=%s",
            predictor.manifest["model_id"], predictor.manifest["trial_id"], predictor.manifest["artifact_version"], canary.prediction_usd,
        )
    except Exception as exc:  # noqa: BLE001 -- fail-closed: any startup failure must leave the service not-ready, never crash-loop silently
        app.state.startup_error = str(exc)
        logger.error("startup failed, service will report not-ready: %s", exc)
    yield


app = FastAPI(title="LAB12 Freight Cost Prediction API (Stage 14, Phase A)", lifespan=lifespan)
for exc_type, handler in EXCEPTION_HANDLERS.items():
    app.add_exception_handler(exc_type, handler)


def get_predictor(request: Request) -> FreightCostPredictor:
    predictor = request.app.state.predictor
    if predictor is None:
        raise HTTPException(status_code=503, detail=f"Service not ready: {request.app.state.startup_error}")
    return predictor


async def _read_json_body(request: Request) -> Any:
    try:
        return await request.json()
    except Exception as exc:  # noqa: BLE001 -- any body-parsing failure is a schema error, not a server error
        from inference.contracts import FeatureSchemaError

        raise FeatureSchemaError(f"INVALID_SHIPMENT_STRUCTURE: request body is not valid JSON ({exc})") from exc


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready(request: Request) -> JSONResponse:
    if request.app.state.ready:
        predictor: FreightCostPredictor = request.app.state.predictor
        return JSONResponse(status_code=200, content={
            "status": "ready",
            "model_id": predictor.manifest["model_id"],
            "trial_id": predictor.manifest["trial_id"],
            "artifact_version": predictor.manifest["artifact_version"],
        })
    return JSONResponse(status_code=503, content={"status": "not_ready", "reason": request.app.state.startup_error})


@app.post("/predict")
async def predict(
    request: Request,
    explain: bool = Query(False),
    request_interval: bool = Query(False),
    predictor: FreightCostPredictor = Depends(get_predictor),
) -> JSONResponse:
    payload = await _read_json_body(request)
    result = predictor.predict_one(payload, explain=explain, request_interval=request_interval)
    _log_result("predict", result)
    return JSONResponse(status_code=200, content=result.to_dict())


@app.post("/predict/batch")
async def predict_batch(
    request: Request,
    explain: bool = Query(False),
    request_interval: bool = Query(False),
    predictor: FreightCostPredictor = Depends(get_predictor),
) -> JSONResponse:
    payload = await _read_json_body(request)
    if not isinstance(payload, list):
        from inference.contracts import FeatureSchemaError

        raise FeatureSchemaError(f"INVALID_SHIPMENT_STRUCTURE: batch endpoint requires a JSON array, got {type(payload).__name__}")
    results = predictor.predict_batch(payload, explain=explain, request_interval=request_interval)
    for result in results:
        _log_result("predict_batch", result)
    return JSONResponse(status_code=200, content=[r.to_dict() for r in results])
