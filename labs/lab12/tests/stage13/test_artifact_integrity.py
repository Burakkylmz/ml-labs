from pathlib import Path

import pytest

from inference.artifact_store import MODEL_FILENAME, compute_sha256, write_bundle
from inference.contracts import ArtifactIntegrityError


def test_bundle_contains_all_required_files(bundle_dir: Path):
    expected = {"model.joblib", "manifest.json", "feature_schema.json", "preprocessing_schema.json", "model_config.json", "environment.json", "reference_predictions.json"}
    actual = {p.name for p in bundle_dir.iterdir()}
    assert expected <= actual


def test_manifest_records_matching_sha256(bundle_dir: Path):
    import json

    manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
    actual_hash = compute_sha256(bundle_dir / MODEL_FILENAME)
    assert manifest["model_artifact_sha256"] == actual_hash


def test_write_bundle_refuses_to_overwrite_existing_version(bundle_dir: Path, fitted_pipeline_and_data):
    pipeline, _df, y = fitted_pipeline_and_data
    with pytest.raises(ArtifactIntegrityError):
        write_bundle(
            fitted_pipeline=pipeline, bundle_version_dir=bundle_dir,
            manifest_fields={"model_id": "M04", "trial_id": "M04-T003", "artifact_version": "v1", "feature_schema_version": "test-v1",
                              "feature_schema_inline": {"numeric": [], "categorical": []}, "reference_stats": {"min_usd": 0.0, "max_usd": 1.0}, "environment": {}},
            feature_schema={}, preprocessing_schema={}, model_config={}, environment={}, reference_predictions={},
        )


def test_corrupted_model_file_fails_checksum(bundle_dir: Path):
    model_path = bundle_dir / MODEL_FILENAME
    original = model_path.read_bytes()
    try:
        model_path.write_bytes(original[:-5] + b"xxxxx")
        import json

        manifest = json.loads((bundle_dir / "manifest.json").read_text(encoding="utf-8"))
        assert compute_sha256(model_path) != manifest["model_artifact_sha256"]
    finally:
        model_path.write_bytes(original)
