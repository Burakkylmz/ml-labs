"""Feature schema validation for Stage 13 inference.

Enforces the frozen Stage 07 Minimal Core feature contract on a single
canonical shipment-level record. Field *presence* and value *missingness*
are deliberately checked separately: a feature being imputable during
preprocessing does not make the field itself optional in the input
contract (see stage13_feature_inference_contract.md).
"""

from __future__ import annotations

import math
from typing import Any

from .contracts import FeatureSchema, FeatureSchemaError, RISK_FLAG_UNKNOWN_CATEGORY


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False


def _coerce_numeric(field_name: str, value: Any) -> float | None:
    if _is_missing(value):
        return None
    if isinstance(value, bool):
        raise FeatureSchemaError(f"INVALID_FIELD_TYPE: '{field_name}' expected numeric, got bool")
    if not isinstance(value, (int, float)):
        raise FeatureSchemaError(f"INVALID_FIELD_TYPE: '{field_name}' expected numeric, got {type(value).__name__} ('{value}') -- no silent string coercion is performed")
    value = float(value)
    if math.isinf(value):
        raise FeatureSchemaError(f"INVALID_NUMERIC_VALUE: '{field_name}' is infinite")
    if math.isnan(value):
        return None
    if value < 0:
        raise FeatureSchemaError(f"INVALID_NUMERIC_VALUE: '{field_name}'={value} is negative, which is not valid for this business quantity")
    return value


def _coerce_categorical(field_name: str, value: Any) -> str | None:
    if _is_missing(value):
        return None
    if not isinstance(value, str):
        raise FeatureSchemaError(f"INVALID_FIELD_TYPE: '{field_name}' expected string, got {type(value).__name__} ('{value}')")
    return value


class FeatureSchemaValidator:
    """Validates a single canonical shipment record against a frozen FeatureSchema."""

    def __init__(self, schema: FeatureSchema, fitted_categories: dict[str, set[str]], strict: bool = True):
        self.schema = schema
        self._fitted_categories = fitted_categories
        self.strict = strict

    def validate(self, record: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Returns (cleaned_record, risk_flags) or raises FeatureSchemaError."""
        if not isinstance(record, dict):
            raise FeatureSchemaError(f"INVALID_SHIPMENT_STRUCTURE: expected a dict, got {type(record).__name__}")

        missing = [f for f in self.schema.required_fields if f not in record]
        if missing:
            raise FeatureSchemaError(f"MISSING_REQUIRED_FIELD: {missing}")

        if self.strict:
            extra = sorted(set(record.keys()) - set(self.schema.required_fields))
            if extra:
                raise FeatureSchemaError(f"UNKNOWN_FIELD: {extra} -- strict schema mode rejects unrecognized fields")

        cleaned: dict[str, Any] = {}
        risk_flags: list[str] = []

        for field_name in self.schema.numeric:
            cleaned[field_name] = _coerce_numeric(field_name, record[field_name])

        for field_name in self.schema.categorical:
            value = _coerce_categorical(field_name, record[field_name])
            cleaned[field_name] = value
            if value is not None:
                known = self._fitted_categories.get(field_name, set())
                if value not in known:
                    risk_flags.append(RISK_FLAG_UNKNOWN_CATEGORY)

        return cleaned, risk_flags
