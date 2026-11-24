def test_explain_false_is_the_default(client, valid_shipment):
    r = client.post("/predict", json=valid_shipment)
    assert r.json()["explanation_status"] == "not_requested"
    assert r.json()["explanation"] is None


def test_explain_true_returns_additive_shap_explanation(client, valid_shipment):
    r = client.post("/predict", json=valid_shipment, params={"explain": "true"})
    body = r.json()
    assert body["explanation_status"] == "available"
    assert body["explanation"] is not None
    assert body["explanation"]["additivity_valid"] is True
    assert abs(body["explanation"]["additivity_diff_usd"]) < 1e-6


def test_explain_true_single_prediction_not_bounded_by_batch_limit(client, valid_shipment):
    """max_batch_explanations only bounds *batch* explain requests; a single /predict
    call with explain=true is always allowed."""
    r = client.post("/predict", json=valid_shipment, params={"explain": "true"})
    assert r.status_code == 200
    assert r.json()["explanation_status"] == "available"
