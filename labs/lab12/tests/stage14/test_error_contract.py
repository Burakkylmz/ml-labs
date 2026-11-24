"""Verifies every exception->HTTP mapping in stage14_api_deployment_contract.md
Section 11, including the two 503 cases that the contract says "should only
occur at startup" -- simulated here via dependency override so the mapping
itself is proven correct even though it is not expected to fire in practice.
"""

import pytest

from api.app import app, get_predictor
from inference.contracts import ArtifactIntegrityError, ModelCompatibilityError, PredictionValidationError


class _RaisingPredictor:
    def __init__(self, exc: Exception):
        self._exc = exc

    def predict_one(self, *args, **kwargs):
        raise self._exc

    def predict_batch(self, *args, **kwargs):
        raise self._exc


@pytest.fixture()
def override_predictor():
    def _apply(exc: Exception):
        app.dependency_overrides[get_predictor] = lambda: _RaisingPredictor(exc)

    yield _apply
    app.dependency_overrides.pop(get_predictor, None)


def test_prediction_validation_error_maps_to_500(client, valid_shipment, override_predictor):
    override_predictor(PredictionValidationError("Model produced a non-finite prediction: nan"))
    r = client.post("/predict", json=valid_shipment)
    assert r.status_code == 500
    assert r.json()["error_code"] == "PREDICTION_VALIDATION_ERROR"


def test_artifact_integrity_error_maps_to_503(client, valid_shipment, override_predictor):
    override_predictor(ArtifactIntegrityError("SHA-256 mismatch for model.joblib"))
    r = client.post("/predict", json=valid_shipment)
    assert r.status_code == 503
    assert r.json()["error_code"] == "ARTIFACT_INTEGRITY_ERROR"


def test_model_compatibility_error_maps_to_503(client, valid_shipment, override_predictor):
    override_predictor(ModelCompatibilityError("sklearn_version mismatch"))
    r = client.post("/predict", json=valid_shipment)
    assert r.status_code == 503
    assert r.json()["error_code"] == "MODEL_COMPATIBILITY_ERROR"


@pytest.mark.parametrize("field_to_drop,expected_code", [
    ("Line_Item_Qty_Sum", "MISSING_REQUIRED_FIELD"),
])
def test_missing_field_error_code(client, valid_shipment, field_to_drop, expected_code):
    payload = dict(valid_shipment)
    del payload[field_to_drop]
    r = client.post("/predict", json=payload)
    assert r.status_code == 422
    assert r.json()["error_code"] == expected_code


def test_unknown_field_rejected(client, valid_shipment):
    r = client.post("/predict", json=dict(valid_shipment, Extra_Field="nope"))
    assert r.status_code == 422
    assert r.json()["error_code"] == "UNKNOWN_FIELD"


def test_invalid_field_type_rejected(client, valid_shipment):
    r = client.post("/predict", json=dict(valid_shipment, Line_Item_Qty_Sum="not-a-number"))
    assert r.status_code == 422
    assert r.json()["error_code"] == "INVALID_FIELD_TYPE"


def test_invalid_shipment_structure_for_non_dict_body(client):
    r = client.post("/predict", json=["not", "a", "dict"])
    assert r.status_code == 422
    assert r.json()["error_code"] == "INVALID_SHIPMENT_STRUCTURE"


def test_error_response_shape_is_uniform(client, valid_shipment):
    payload = dict(valid_shipment)
    del payload["Country"]
    r = client.post("/predict", json=payload)
    assert set(r.json().keys()) == {"error_code", "detail"}
