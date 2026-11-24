import pandas as pd
import pytest

from evaluation import population


def test_label_eligibility_handling_excludes_reference_only_and_ambiguous_groups(synthetic_raw_df):
    """SHIP-C (reference-only, no numeric row) and SHIP-D (two numeric rows,
    ambiguous anchor) must both be excluded; clean single-anchor shipments
    must be included with their correct numeric target."""
    targets = population.resolve_shipment_targets(synthetic_raw_df)
    keys = set(targets["Shipment_Key"])
    assert "SHIP-C" not in keys  # no numeric anchor
    assert "SHIP-D" not in keys  # ambiguous (2 numeric rows)
    assert "SHIP-A" in keys and "SHIP-B" in keys

    ship_a_target = targets.loc[targets["Shipment_Key"] == "SHIP-A", "Target"].iloc[0]
    assert ship_a_target == pytest.approx(1200.50)
    ship_b_target = targets.loc[targets["Shipment_Key"] == "SHIP-B", "Target"].iloc[0]
    assert ship_b_target == pytest.approx(3400.00)  # the numeric row only, not the reference row


def test_shipment_key_alignment_between_targets_and_features(synthetic_raw_df):
    """Targets and aggregated features must align on the SAME shipment keys
    -- no row from one side can silently fail to match the other."""
    targets = population.resolve_shipment_targets(synthetic_raw_df)
    features = population.resolve_shipment_features(synthetic_raw_df)
    merged = targets.merge(features, on="Shipment_Key", how="inner")
    assert len(merged) == len(targets)  # every eligible-target shipment has features
    assert set(merged.columns) >= {"Shipment_Key", "Target", "Line_Item_Qty_Sum", "Line_Item_Value_Sum", "Shipment_Mode", "INCO_Term", "Country", "Product_Group"}


def test_feature_aggregation_sums_numeric_and_takes_first_categorical(synthetic_raw_df):
    features = population.resolve_shipment_features(synthetic_raw_df)
    ship_b = features.loc[features["Shipment_Key"] == "SHIP-B"].iloc[0]
    assert ship_b["Line_Item_Qty_Sum"] == pytest.approx(80)  # 50 + 30
    assert ship_b["Line_Item_Value_Sum"] == pytest.approx(10000)  # 8000 + 2000
    assert ship_b["Shipment_Mode"] == "Ocean"


def test_load_development_population_filters_to_train_split_only(synthetic_dataset_csv, synthetic_split_manifest):
    dev = population.load_development_population(synthetic_dataset_csv, synthetic_split_manifest)
    assert set(dev["Shipment_Key"]) == {"SHIP-A", "SHIP-B", "SHIP-E", "SHIP-F", "SHIP-H"}
    assert "SHIP-G" not in set(dev["Shipment_Key"])  # Protected_Test, must not leak into development


def test_load_protected_population_requires_a_valid_unlock_token(synthetic_dataset_csv, synthetic_split_manifest):
    with pytest.raises(PermissionError):
        population.load_protected_population(synthetic_dataset_csv, synthetic_split_manifest, unlock_token=None)

    class _FakeToken:
        def is_valid(self):
            return True

    with pytest.raises(PermissionError):
        population.load_protected_population(synthetic_dataset_csv, synthetic_split_manifest, unlock_token=_FakeToken())
