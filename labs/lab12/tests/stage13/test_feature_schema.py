import pytest

from inference.contracts import FeatureSchema, FeatureSchemaError
from inference.schemas import FeatureSchemaValidator

SCHEMA = FeatureSchema(
    numeric=("Line_Item_Qty_Sum", "Line_Item_Value_Sum"),
    categorical=("Shipment_Mode", "INCO_Term", "Country", "Product_Group"),
    schema_version="test-v1",
)
FITTED_CATEGORIES = {
    "Shipment_Mode": {"Air", "Ocean", "Truck"},
    "INCO_Term": {"EXW", "DDP", "CIP"},
    "Country": {"Nigeria", "Kenya", "Uganda"},
    "Product_Group": {"ARV", "HRDT"},
}


@pytest.fixture()
def validator():
    return FeatureSchemaValidator(SCHEMA, FITTED_CATEGORIES, strict=True)


@pytest.fixture()
def valid_record():
    return {"Line_Item_Qty_Sum": 500.0, "Line_Item_Value_Sum": 20000.0, "Shipment_Mode": "Air", "INCO_Term": "EXW", "Country": "Nigeria", "Product_Group": "ARV"}


def test_valid_input_accepted(validator, valid_record):
    cleaned, flags = validator.validate(valid_record)
    assert cleaned["Line_Item_Qty_Sum"] == 500.0
    assert flags == []


def test_missing_required_feature_rejected(validator, valid_record):
    del valid_record["Country"]
    with pytest.raises(FeatureSchemaError, match="MISSING_REQUIRED_FIELD"):
        validator.validate(valid_record)


def test_allowed_null_categorical_accepted(validator, valid_record):
    valid_record["Country"] = None
    cleaned, _flags = validator.validate(valid_record)
    assert cleaned["Country"] is None


def test_allowed_null_numeric_accepted(validator, valid_record):
    valid_record["Line_Item_Qty_Sum"] = None
    cleaned, _flags = validator.validate(valid_record)
    assert cleaned["Line_Item_Qty_Sum"] is None


def test_invalid_numeric_type_rejected(validator, valid_record):
    valid_record["Line_Item_Qty_Sum"] = "ten thousand"
    with pytest.raises(FeatureSchemaError, match="INVALID_FIELD_TYPE"):
        validator.validate(valid_record)


def test_nan_numeric_treated_as_missing(validator, valid_record):
    valid_record["Line_Item_Qty_Sum"] = float("nan")
    cleaned, _flags = validator.validate(valid_record)
    assert cleaned["Line_Item_Qty_Sum"] is None


def test_infinite_numeric_rejected(validator, valid_record):
    valid_record["Line_Item_Qty_Sum"] = float("inf")
    with pytest.raises(FeatureSchemaError, match="INVALID_NUMERIC_VALUE"):
        validator.validate(valid_record)


def test_negative_numeric_rejected(validator, valid_record):
    valid_record["Line_Item_Value_Sum"] = -1.0
    with pytest.raises(FeatureSchemaError, match="INVALID_NUMERIC_VALUE"):
        validator.validate(valid_record)


def test_unknown_category_flagged_not_rejected(validator, valid_record):
    valid_record["Country"] = "Atlantis"
    cleaned, flags = validator.validate(valid_record)
    assert cleaned["Country"] == "Atlantis"
    assert "UNKNOWN_CATEGORY" in flags


def test_extra_field_rejected_in_strict_mode(validator, valid_record):
    valid_record["Freight Cost (USD)"] = 9999.0
    with pytest.raises(FeatureSchemaError, match="UNKNOWN_FIELD"):
        validator.validate(valid_record)


def test_reordered_keys_produce_identical_cleaned_record(validator, valid_record):
    reordered = {k: valid_record[k] for k in reversed(list(valid_record.keys()))}
    cleaned_a, _ = validator.validate(valid_record)
    cleaned_b, _ = validator.validate(reordered)
    assert cleaned_a == cleaned_b


def test_non_dict_structure_rejected(validator):
    with pytest.raises(FeatureSchemaError, match="INVALID_SHIPMENT_STRUCTURE"):
        validator.validate(["not", "a", "dict"])  # type: ignore[arg-type]
