from pathlib import Path

import pytest

from inference.contracts import ArtifactIntegrityError, ModelCompatibilityError
from inference.model_loader import TrustedBundleLoader


def test_trusted_load_succeeds(bundle_dir: Path, allowed_root: Path):
    loader = TrustedBundleLoader(allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="M04-T003")
    pipeline, manifest = loader.load(bundle_dir)
    assert manifest["model_id"] == "M04"
    assert hasattr(pipeline, "predict")


def test_wrong_model_id_rejected(bundle_dir: Path, allowed_root: Path):
    loader = TrustedBundleLoader(allowed_root=allowed_root, expected_model_id="WRONG", expected_trial_id="M04-T003")
    with pytest.raises(ArtifactIntegrityError):
        loader.load(bundle_dir)


def test_wrong_trial_id_rejected(bundle_dir: Path, allowed_root: Path):
    loader = TrustedBundleLoader(allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="WRONG-TRIAL")
    with pytest.raises(ArtifactIntegrityError):
        loader.load(bundle_dir)


def test_tampered_model_file_rejected(bundle_dir: Path, allowed_root: Path):
    model_path = bundle_dir / "model.joblib"
    original = model_path.read_bytes()
    try:
        model_path.write_bytes(original[:-5] + b"xxxxx")
        loader = TrustedBundleLoader(allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="M04-T003")
        with pytest.raises(ArtifactIntegrityError):
            loader.load(bundle_dir)
    finally:
        model_path.write_bytes(original)


def test_missing_manifest_rejected(bundle_dir: Path, allowed_root: Path):
    (bundle_dir / "manifest.json").unlink()
    loader = TrustedBundleLoader(allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="M04-T003")
    with pytest.raises(ArtifactIntegrityError):
        loader.load(bundle_dir)


def test_untrusted_path_outside_allowed_root_rejected(bundle_dir: Path, tmp_path_factory):
    other_root = tmp_path_factory.mktemp("other_root")
    loader = TrustedBundleLoader(allowed_root=other_root, expected_model_id="M04", expected_trial_id="M04-T003")
    with pytest.raises(ArtifactIntegrityError):
        loader.load(bundle_dir)


def test_sklearn_version_mismatch_rejected(bundle_dir: Path, allowed_root: Path):
    import json

    manifest_path = bundle_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["environment"]["sklearn_version"] = "0.0.0-incompatible"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    loader = TrustedBundleLoader(allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="M04-T003")
    with pytest.raises(ModelCompatibilityError):
        loader.load(bundle_dir)


def test_python_major_minor_mismatch_rejected(bundle_dir: Path, allowed_root: Path):
    import json

    manifest_path = bundle_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["environment"]["python_version"] = "3.9.0"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    loader = TrustedBundleLoader(allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="M04-T003")
    with pytest.raises(ModelCompatibilityError):
        loader.load(bundle_dir)


def test_python_patch_version_difference_tolerated(bundle_dir: Path, allowed_root: Path):
    """A bundle recorded with a different PATCH release of the same Python minor series
    (e.g. 3.11.15 vs the runtime's 3.11.18) must load successfully -- joblib/pickle
    compatibility within a minor series is not affected by the patch version."""
    import json
    import sys

    manifest_path = bundle_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current_minor = ".".join(sys.version.split()[0].split(".")[:2])
    manifest["environment"]["python_version"] = f"{current_minor}.0"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    loader = TrustedBundleLoader(allowed_root=allowed_root, expected_model_id="M04", expected_trial_id="M04-T003")
    pipeline, loaded_manifest = loader.load(bundle_dir)
    assert hasattr(pipeline, "predict")
