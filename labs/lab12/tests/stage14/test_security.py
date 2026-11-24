"""stage14_api_deployment_contract.md Section 15: the API must not accept
an arbitrary, user-supplied model/bundle path from any request surface."""

import inspect

from api import config


def test_bundle_path_is_a_fixed_constant_not_environment_derived():
    source = inspect.getsource(config)
    assert "os.environ" not in source
    assert "getenv" not in source


def test_bundle_version_dir_resolves_inside_allowed_root():
    config.BUNDLE_VERSION_DIR.resolve().relative_to(config.BUNDLE_ROOT.resolve())
    config.BUNDLE_ROOT.resolve().relative_to(config.ARTIFACT_ROOT.resolve())


def test_request_cannot_override_bundle_path_via_body_field(client, valid_shipment):
    """A 'model_path'/'bundle_path' field is not part of the frozen schema, so strict
    validation must reject it exactly like any other unknown field -- there is no
    code path through which a caller can redirect the loader."""
    tampered = dict(valid_shipment, model_path="/etc/passwd")
    r = client.post("/predict", json=tampered)
    assert r.status_code == 422
    assert r.json()["error_code"] == "UNKNOWN_FIELD"


def test_request_cannot_override_bundle_path_via_query_param(client, valid_shipment):
    """An unrecognized query parameter is simply ignored by FastAPI's routing (not
    bound to any handler argument); it cannot reach the fixed loader configuration."""
    r = client.post("/predict", json=valid_shipment, params={"bundle_path": "../../etc/passwd"})
    assert r.status_code == 200
    assert r.json()["model_id"] == "M04"


def test_no_endpoint_exposes_a_path_parameter():
    path_params = [
        param for route in __import__("api.app", fromlist=["app"]).app.routes
        for param in getattr(route, "param_convertors", {})
    ]
    assert path_params == []
