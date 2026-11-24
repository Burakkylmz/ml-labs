def test_health_always_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready_reports_loaded_bundle_identity(client):
    r = client.get("/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ready"
    assert body["model_id"] == "M04"
    assert body["trial_id"] == "M04-T003"
    assert body["artifact_version"] == "v1"


def test_predict_dependency_rejects_when_not_loaded():
    """get_predictor must fail-closed (503) whenever app.state.predictor is unset -- the
    startup-failure path, exercised directly rather than via a shared module-level app
    singleton (whose lifespan state is order-dependent across tests)."""
    import types

    import pytest
    from fastapi import HTTPException

    from api.app import get_predictor

    fake_app_state = types.SimpleNamespace(predictor=None, startup_error="bundle load failed: simulated")
    fake_request = types.SimpleNamespace(app=types.SimpleNamespace(state=fake_app_state))

    with pytest.raises(HTTPException) as exc_info:
        get_predictor(fake_request)
    assert exc_info.value.status_code == 503
    assert "simulated" in exc_info.value.detail
