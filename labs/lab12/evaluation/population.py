"""Development (2006-2013) and Protected (2015) population loaders.

Both loaders share the same shipment-level target resolution (Stage 03.5:
group by `ASN/DN #`, take the group's single numeric Freight Cost row --
every eligible shipment group has exactly one, per the shipment-level
dataset contract) and the same split source (`stage05_split_manifest.csv`,
which carries no target values at all). The only difference is which
`Split` label they filter to.

**Structural protection, not just convention:** `load_protected_population`
requires an `evaluation.gate.UnlockToken`, a frozen object that only
`PreUnlockGate.unlock()` can construct. There is no way to call it from a
pytest collection or a normal notebook cell without having already passed
every pre-unlock check in `gate.py`. This preparation task never
constructs an `UnlockToken`, so this function is never actually called
against the real dataset in this task.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from .contracts import (
    DEVELOPMENT_SPLIT_LABEL,
    GROUPING_KEY,
    PROTECTED_SPLIT_LABEL,
    REQUIRED_SCHEMA_FIELDS,
    TARGET_COLUMN_RAW,
)

if TYPE_CHECKING:
    from .gate import UnlockToken

# Raw-column -> Minimal Core feature aggregation (Stage 07 Section on
# aggregation semantics: numeric -> sum(), categorical -> first()). This is
# feature AGGREGATION (row-level line items -> shipment-level record), a
# step upstream of and distinct from Stage 13's inference contract, which
# already assumes a shipment-level record (D-146: no feature_adapter
# needed THERE because the API never sees raw line items). Evaluation
# does see raw line items, so this adapter belongs here, not in `inference/`.
_NUMERIC_SUM_COLUMNS = {"Line_Item_Qty_Sum": "Line Item Quantity", "Line_Item_Value_Sum": "Line Item Value"}
_CATEGORICAL_FIRST_COLUMNS = {"Shipment_Mode": "Shipment Mode", "INCO_Term": "Vendor INCO Term", "Country": "Country", "Product_Group": "Product Group"}


def resolve_shipment_targets(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Group-level numeric target resolution (Stage 03.5 policy).

    Returns one row per shipment group with a resolved numeric target --
    groups with zero or more than one numeric Freight Cost row are
    excluded (not eligible; see shipment_group_profile.csv's
    Has_Numeric_Target / Numeric_Anchor_Count invariants)."""
    working = raw_df.copy()
    working["_numeric_target"] = pd.to_numeric(working[TARGET_COLUMN_RAW], errors="coerce")
    numeric_rows = working[working["_numeric_target"].notna()]
    anchor_counts = numeric_rows.groupby("ASN/DN #").size()
    single_anchor_groups = anchor_counts[anchor_counts == 1].index
    eligible = numeric_rows[numeric_rows["ASN/DN #"].isin(single_anchor_groups)]
    resolved = eligible.drop_duplicates("ASN/DN #")[["ASN/DN #", "_numeric_target"]]
    return resolved.rename(columns={"ASN/DN #": GROUPING_KEY, "_numeric_target": "Target"})


def resolve_shipment_features(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Shipment-level Minimal Core feature aggregation (Stage 07 semantics):
    numeric raw columns summed per shipment group, categorical raw columns
    take the group's first (repeated-per-row) value."""
    grouped = raw_df.groupby("ASN/DN #")
    aggregated = {}
    for feature_name, raw_column in _NUMERIC_SUM_COLUMNS.items():
        aggregated[feature_name] = grouped[raw_column].sum()
    for feature_name, raw_column in _CATEGORICAL_FIRST_COLUMNS.items():
        aggregated[feature_name] = grouped[raw_column].first()
    result = pd.DataFrame(aggregated).reset_index().rename(columns={"ASN/DN #": GROUPING_KEY})
    assert set(REQUIRED_SCHEMA_FIELDS) <= set(result.columns), "resolve_shipment_features did not produce every Minimal Core field"
    return result


def _load_split_members(split_manifest_path: Path, split_label: str) -> pd.DataFrame:
    manifest = pd.read_csv(split_manifest_path)
    return manifest[manifest["Split"] == split_label][[GROUPING_KEY]]


def load_development_population(dataset_path: Path, split_manifest_path: Path) -> pd.DataFrame:
    """The 2006-2013 eligible training population (expected n=4987), with
    both the resolved target AND the Minimal Core features -- B1 only
    needs `Target`, B4 needs `Shipment_Mode`/`INCO_Term` too.

    Safe by construction: filters to `Split == "Train"` only. No caller in
    this codebase passes a protected-period path to this function."""
    raw_df = pd.read_csv(dataset_path, encoding="latin-1")
    targets = resolve_shipment_targets(raw_df)
    features = resolve_shipment_features(raw_df)
    train_members = _load_split_members(split_manifest_path, DEVELOPMENT_SPLIT_LABEL)
    return train_members.merge(targets, on=GROUPING_KEY, how="inner").merge(features, on=GROUPING_KEY, how="inner")


def load_protected_population(dataset_path: Path, split_manifest_path: Path, *, unlock_token: "UnlockToken") -> pd.DataFrame:
    """The 2015 Protected Test population (target + Minimal Core features).
    UNREACHABLE without a valid `UnlockToken` from `gate.PreUnlockGate.unlock()`
    -- see module docstring."""
    from .gate import UnlockToken

    if not isinstance(unlock_token, UnlockToken) or not unlock_token.is_valid():
        raise PermissionError("load_protected_population requires a valid UnlockToken from PreUnlockGate.unlock()")

    raw_df = pd.read_csv(dataset_path, encoding="latin-1")
    targets = resolve_shipment_targets(raw_df)
    features = resolve_shipment_features(raw_df)
    protected_members = _load_split_members(split_manifest_path, PROTECTED_SPLIT_LABEL)
    return protected_members.merge(targets, on=GROUPING_KEY, how="inner").merge(features, on=GROUPING_KEY, how="inner")
