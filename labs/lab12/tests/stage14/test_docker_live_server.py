"""The 'Docker service integration tests' layer required by
stage14_api_deployment_contract.md Section 16: a real `uvicorn` process
bound to a real TCP port, reached over real HTTP -- as opposed to the
in-process ASGI TestClient used by every other test module here. Run
identically on the host and inside the `ml-lab` container; the Stage 14
Phase A report records both runs separately.
"""

import httpx


def test_live_server_health_and_ready(live_server):
    r = httpx.get(f"{live_server}/health", timeout=5.0)
    assert r.status_code == 200 and r.json() == {"status": "ok"}

    r = httpx.get(f"{live_server}/ready", timeout=5.0)
    assert r.status_code == 200
    assert r.json()["model_id"] == "M04"


def test_live_server_predict_over_real_http(live_server, valid_shipment):
    r = httpx.post(f"{live_server}/predict", json=valid_shipment, timeout=10.0)
    assert r.status_code == 200
    body = r.json()
    assert body["prediction_validity"] == "valid"
    assert body["model_id"] == "M04"


def test_live_server_batch_over_real_http(live_server, valid_shipment):
    r = httpx.post(f"{live_server}/predict/batch", json=[valid_shipment] * 5, timeout=10.0)
    assert r.status_code == 200
    assert len(r.json()) == 5


def test_live_server_error_contract_over_real_http(live_server, valid_shipment):
    bad = dict(valid_shipment)
    del bad["Country"]
    r = httpx.post(f"{live_server}/predict", json=bad, timeout=10.0)
    assert r.status_code == 422
    assert r.json()["error_code"] == "MISSING_REQUIRED_FIELD"


def test_live_server_handles_concurrent_requests(live_server, valid_shipment):
    """A minimal concurrency smoke test -- the single, startup-loaded predictor instance
    must serve multiple simultaneous requests without raising (no per-request refitting,
    no shared mutable state corruption)."""
    import concurrent.futures

    def _call(i: int):
        shipment = dict(valid_shipment, Line_Item_Qty_Sum=float(100 + i))
        return httpx.post(f"{live_server}/predict", json=shipment, timeout=10.0).status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        statuses = list(pool.map(_call, range(20)))
    assert all(status == 200 for status in statuses)
