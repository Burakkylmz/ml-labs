"""Versioned model bundle persistence for Stage 13.

Writes a fitted pipeline plus its manifest, feature schema, preprocessing
schema, model config, environment metadata, and reference predictions as a
single immutable, versioned directory. Overwriting an existing version is
refused -- a changed artifact must go to a new version directory.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import joblib

from .contracts import ArtifactIntegrityError

MODEL_FILENAME = "model.joblib"
MANIFEST_FILENAME = "manifest.json"
FEATURE_SCHEMA_FILENAME = "feature_schema.json"
PREPROCESSING_SCHEMA_FILENAME = "preprocessing_schema.json"
MODEL_CONFIG_FILENAME = "model_config.json"
ENVIRONMENT_FILENAME = "environment.json"
REFERENCE_PREDICTIONS_FILENAME = "reference_predictions.json"

REQUIRED_BUNDLE_FILES = (
    MODEL_FILENAME,
    MANIFEST_FILENAME,
    FEATURE_SCHEMA_FILENAME,
    PREPROCESSING_SCHEMA_FILENAME,
    MODEL_CONFIG_FILENAME,
    ENVIRONMENT_FILENAME,
    REFERENCE_PREDICTIONS_FILENAME,
)


def compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_bundle(
    *,
    fitted_pipeline: Any,
    bundle_version_dir: Path,
    manifest_fields: dict[str, Any],
    feature_schema: dict[str, Any],
    preprocessing_schema: dict[str, Any],
    model_config: dict[str, Any],
    environment: dict[str, Any],
    reference_predictions: dict[str, Any],
) -> dict[str, Any]:
    """Atomically writes a complete bundle to bundle_version_dir. Refuses to overwrite."""
    if bundle_version_dir.exists() and any(bundle_version_dir.iterdir()):
        raise ArtifactIntegrityError(
            f"Refusing to overwrite existing non-empty bundle version directory: {bundle_version_dir} "
            "-- create a new version directory instead."
        )

    bundle_version_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=str(bundle_version_dir.parent)) as tmp:
        tmp_path = Path(tmp)
        model_path = tmp_path / MODEL_FILENAME
        joblib.dump(fitted_pipeline, model_path)
        model_sha256 = compute_sha256(model_path)

        manifest = dict(manifest_fields)
        manifest["model_artifact_sha256"] = model_sha256
        manifest["bundle_files"] = list(REQUIRED_BUNDLE_FILES)

        (tmp_path / MANIFEST_FILENAME).write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        (tmp_path / FEATURE_SCHEMA_FILENAME).write_text(json.dumps(feature_schema, indent=2, ensure_ascii=False), encoding="utf-8")
        (tmp_path / PREPROCESSING_SCHEMA_FILENAME).write_text(json.dumps(preprocessing_schema, indent=2, ensure_ascii=False), encoding="utf-8")
        (tmp_path / MODEL_CONFIG_FILENAME).write_text(json.dumps(model_config, indent=2, ensure_ascii=False), encoding="utf-8")
        (tmp_path / ENVIRONMENT_FILENAME).write_text(json.dumps(environment, indent=2, ensure_ascii=False), encoding="utf-8")
        (tmp_path / REFERENCE_PREDICTIONS_FILENAME).write_text(json.dumps(reference_predictions, indent=2, ensure_ascii=False), encoding="utf-8")

        # Finalize: move the fully-written temp directory into place as one atomic step.
        # (bundle_version_dir was confirmed absent-or-empty above; remove it first if it
        # pre-exists empty, so shutil.move performs a clean rename rather than nesting.)
        if bundle_version_dir.exists():
            bundle_version_dir.rmdir()
        shutil.move(str(tmp_path), str(bundle_version_dir))

    return manifest
