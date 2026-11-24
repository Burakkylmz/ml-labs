"""stage14_api_deployment_contract.md Section 9: request_interval=true must
never surface lower/upper bounds through the API -- Stage 12's "Production
Interval Not Approved" decision is carried through unchanged (D-153)."""


def test_request_interval_true_adds_flag_only(client, valid_shipment):
    r = client.post("/predict", json=valid_shipment, params={"request_interval": "true"})
    body = r.json()
    assert body["uncertainty_status"] == "disabled"
    assert "INTERVAL_NOT_APPROVED" in body["risk_flags"]
    assert "lower_bound_usd" not in body
    assert "upper_bound_usd" not in body
    assert "interval" not in body


def test_request_interval_false_omits_flag(client, valid_shipment):
    r = client.post("/predict", json=valid_shipment, params={"request_interval": "false"})
    assert "INTERVAL_NOT_APPROVED" not in r.json()["risk_flags"]


def test_request_interval_applies_to_batch_too(client, valid_shipment):
    r = client.post("/predict/batch", json=[valid_shipment, valid_shipment], params={"request_interval": "true"})
    for row in r.json():
        assert "INTERVAL_NOT_APPROVED" in row["risk_flags"]
        assert "lower_bound_usd" not in row and "upper_bound_usd" not in row
