from api.config import MAX_BATCH_EXPLANATIONS, MAX_BATCH_SIZE


def test_empty_batch_returns_empty_list(client):
    r = client.post("/predict/batch", json=[])
    assert r.status_code == 200
    assert r.json() == []


def test_batch_matches_sequential_single_predictions(client, valid_shipment):
    """Tolerance-based, not exact `==` (D-154 precedent): batch-of-N and N sequential
    batch-of-1 calls hit ExtraTrees' `n_jobs=2` prediction averaging with different
    array shapes, which can differ by ~1e-12 USD due to thread-order-dependent
    floating-point summation -- not a correctness bug, see stage14 D-162."""
    shipments = [dict(valid_shipment, Line_Item_Qty_Sum=float(q)) for q in (100, 500, 5000)]
    batch_resp = client.post("/predict/batch", json=shipments).json()
    single_resp = [client.post("/predict", json=s).json()["prediction_usd"] for s in shipments]
    for batch_val, single_val in zip([r["prediction_usd"] for r in batch_resp], single_resp):
        assert abs(batch_val - single_val) < 1e-6


def test_atomic_batch_validation_rejects_whole_batch_on_one_bad_row(client, valid_shipment):
    bad_row = dict(valid_shipment)
    del bad_row["Country"]
    r = client.post("/predict/batch", json=[valid_shipment, bad_row, valid_shipment])
    assert r.status_code == 422
    assert r.json()["error_code"] == "MISSING_REQUIRED_FIELD"


def test_batch_size_exceeded_rejected(client, valid_shipment):
    r = client.post("/predict/batch", json=[valid_shipment] * (MAX_BATCH_SIZE + 1))
    assert r.status_code == 422
    assert r.json()["error_code"] == "BATCH_SIZE_EXCEEDED"


def test_batch_size_at_limit_accepted(client, valid_shipment):
    r = client.post("/predict/batch", json=[valid_shipment] * MAX_BATCH_SIZE)
    assert r.status_code == 200
    assert len(r.json()) == MAX_BATCH_SIZE


def test_batch_not_a_json_array_rejected(client, valid_shipment):
    r = client.post("/predict/batch", json=valid_shipment)
    assert r.status_code == 422
    assert r.json()["error_code"] == "INVALID_SHIPMENT_STRUCTURE"


def test_explanation_batch_limit_enforced(client, valid_shipment):
    r = client.post("/predict/batch", json=[valid_shipment] * (MAX_BATCH_EXPLANATIONS + 1), params={"explain": "true"})
    assert r.status_code == 422
    assert r.json()["error_code"] == "EXPLANATION_BATCH_LIMIT_EXCEEDED"


def test_explanation_batch_at_limit_accepted(client, valid_shipment):
    r = client.post("/predict/batch", json=[valid_shipment] * MAX_BATCH_EXPLANATIONS, params={"explain": "true"})
    assert r.status_code == 200
    assert all(row["explanation_status"] == "available" for row in r.json())
