import math


def test_valid_shipment_returns_200_with_full_contract(client, valid_shipment):
    r = client.post("/predict", json=valid_shipment)
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {
        "model_id", "trial_id", "model_version", "prediction_usd", "prediction_validity",
        "uncertainty_status", "explanation_status", "explanation", "risk_flags", "invalid_reason",
    }
    assert body["model_id"] == "M04"
    assert body["trial_id"] == "M04-T003"
    assert body["prediction_validity"] == "valid"
    assert body["uncertainty_status"] == "disabled"
    assert body["explanation_status"] == "not_requested"
    assert body["invalid_reason"] is None
    assert math.isfinite(body["prediction_usd"]) and body["prediction_usd"] > 0


def test_missing_values_allowed_missing_fields_rejected(client, valid_shipment):
    """Field presence is required for all Minimal Core features; a NaN/None *value* is
    not the same contract violation as a missing *field* (D-145)."""
    with_null_value = dict(valid_shipment, Country=None)
    r = client.post("/predict", json=with_null_value)
    assert r.status_code == 200

    missing_field = dict(valid_shipment)
    del missing_field["Country"]
    r = client.post("/predict", json=missing_field)
    assert r.status_code == 422
    assert r.json()["error_code"] == "MISSING_REQUIRED_FIELD"


def test_unknown_category_flagged_but_still_predicts(client, valid_shipment):
    r = client.post("/predict", json=dict(valid_shipment, Country="Atlantis"))
    assert r.status_code == 200
    assert "UNKNOWN_CATEGORY" in r.json()["risk_flags"]


def test_negative_numeric_value_rejected(client, valid_shipment):
    r = client.post("/predict", json=dict(valid_shipment, Line_Item_Qty_Sum=-5))
    assert r.status_code == 422
    assert r.json()["error_code"] == "INVALID_NUMERIC_VALUE"
